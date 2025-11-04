"""
Multi-Provider AI Support
Support for Gemini, Claude, OpenAI, Groq
"""
import os
from typing import Dict, Optional, List
from enum import Enum

class AIProvider(str, Enum):
    GEMINI = "gemini"
    CLAUDE = "claude"
    OPENAI = "openai"
    GROQ = "groq"

class MultiProviderAI:
    """Support multiple AI providers with dynamic switching"""
    
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.claude_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        
        # Default provider
        self.default_provider = self._get_default_provider()
    
    def _get_default_provider(self) -> AIProvider:
        """Determine default provider based on available keys"""
        if self.gemini_key:
            return AIProvider.GEMINI
        elif self.groq_key:
            return AIProvider.GROQ
        elif self.claude_key:
            return AIProvider.CLAUDE
        elif self.openai_key:
            return AIProvider.OPENAI
        return AIProvider.GEMINI  # Fallback
    
    async def generate(self, prompt: str, provider: Optional[AIProvider] = None) -> Dict:
        """Generate using specified provider or default"""
        provider = provider or self.default_provider
        
        try:
            if provider == AIProvider.GEMINI:
                return await self._generate_gemini(prompt)
            elif provider == AIProvider.CLAUDE:
                return await self._generate_claude(prompt)
            elif provider == AIProvider.OPENAI:
                return await self._generate_openai(prompt)
            elif provider == AIProvider.GROQ:
                return await self._generate_groq(prompt)
            else:
                return {"success": False, "error": f"Unknown provider: {provider}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_gemini(self, prompt: str) -> Dict:
        """Generate using Google Gemini"""
        if not self.gemini_key:
            return {"success": False, "error": "GEMINI_API_KEY not set"}
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            
            return {
                "success": True,
                "text": response.text,
                "provider": "gemini",
                "model": "gemini-2.0-flash"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "provider": "gemini"}
    
    async def _generate_claude(self, prompt: str) -> Dict:
        """Generate using Anthropic Claude"""
        if not self.claude_key:
            return {"success": False, "error": "ANTHROPIC_API_KEY not set"}
        
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.claude_key)
            
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "success": True,
                "text": message.content[0].text,
                "provider": "claude",
                "model": "claude-3-5-sonnet"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "provider": "claude"}
    
    async def _generate_openai(self, prompt: str) -> Dict:
        """Generate using OpenAI"""
        if not self.openai_key:
            return {"success": False, "error": "OPENAI_API_KEY not set"}
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_key)
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "success": True,
                "text": response.choices[0].message.content,
                "provider": "openai",
                "model": "gpt-4-turbo"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "provider": "openai"}
    
    async def _generate_groq(self, prompt: str) -> Dict:
        """Generate using Groq"""
        if not self.groq_key:
            return {"success": False, "error": "GROQ_API_KEY not set"}
        
        try:
            from groq import Groq
            client = Groq(api_key=self.groq_key)
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "success": True,
                "text": response.choices[0].message.content,
                "provider": "groq",
                "model": "llama-3.3-70b"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "provider": "groq"}
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers based on API keys"""
        providers = []
        if self.gemini_key:
            providers.append("gemini")
        if self.claude_key:
            providers.append("claude")
        if self.openai_key:
            providers.append("openai")
        if self.groq_key:
            providers.append("groq")
        return providers
