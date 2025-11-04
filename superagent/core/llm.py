"""LLM interface for SuperAgent using Claude 3.5 Sonnet."""

import asyncio
from typing import List, Dict, Any, Optional
from anthropic import AsyncAnthropic
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger()


class LLMProvider:
    """High-performance LLM provider using Claude 3.5 Sonnet."""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022",
                 temperature: float = 0.7, max_tokens: int = 8000):
        """Initialize LLM provider.
        
        Args:
            api_key: Anthropic API key
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.total_tokens_used = 0
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def generate(self, prompt: str, system: Optional[str] = None,
                      temperature: Optional[float] = None,
                      max_tokens: Optional[int] = None) -> str:
        """Generate completion from prompt.
        
        Args:
            prompt: User prompt
            system: System prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            Generated text
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens,
            }
            
            if system:
                kwargs["system"] = system
            
            logger.info(f"Generating with {self.model}", prompt_length=len(prompt))
            
            response = await self.client.messages.create(**kwargs)
            
            self.total_tokens_used += response.usage.input_tokens + response.usage.output_tokens
            
            logger.info(
                "Generation complete",
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                total_tokens=self.total_tokens_used
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise
    
    async def generate_batch(self, prompts: List[str], 
                           system: Optional[str] = None) -> List[str]:
        """Generate completions for multiple prompts in parallel.
        
        Args:
            prompts: List of prompts
            system: System prompt
            
        Returns:
            List of generated texts
        """
        tasks = [self.generate(prompt, system) for prompt in prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        outputs = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch generation error for prompt {i}: {result}")
                outputs.append("")
            else:
                outputs.append(result)
        
        return outputs
    
    async def generate_structured(self, prompt: str, 
                                 schema: Dict[str, Any],
                                 system: Optional[str] = None) -> Dict[str, Any]:
        """Generate structured output based on schema.
        
        Args:
            prompt: User prompt
            schema: JSON schema for output
            system: System prompt
            
        Returns:
            Structured data matching schema
        """
        structured_prompt = f"""
{prompt}

Please provide your response in the following JSON format:
{schema}

Ensure your response is valid JSON that matches the schema exactly.
"""
        
        response = await self.generate(structured_prompt, system)
        
        # Extract JSON from response
        import json
        try:
            # Try to find JSON in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse structured output: {e}")
            return {}
    
    async def stream_generate(self, prompt: str, 
                            system: Optional[str] = None):
        """Generate completion with streaming.
        
        Args:
            prompt: User prompt
            system: System prompt
            
        Yields:
            Text chunks
        """
        messages = [{"role": "user", "content": prompt}]
        
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        
        if system:
            kwargs["system"] = system
        
        async with self.client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            "total_tokens_used": self.total_tokens_used,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }





