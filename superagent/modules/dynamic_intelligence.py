"""
Dynamic Intelligence - Enhanced AI Reasoning
Features:
- Extended Thinking: Multi-step reasoning and analysis
- High Power Mode: Upgrade to advanced AI models
- Adaptive model selection based on task complexity
"""

import logging
from typing import Dict, List, Optional
import os

# Optional import - gracefully handle if not installed
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

logger = logging.getLogger(__name__)


class DynamicIntelligence:
    """
    Enhanced AI capabilities with adaptive model selection
    """
    
    def __init__(self):
        self.extended_thinking_enabled = False
        self.high_power_mode = False
        
        # Model tiers
        self.models = {
            'standard': 'gemini-2.0-flash',
            'high_power': 'gemini-2.0-flash-thinking-exp',  # Advanced thinking model
            'extended': 'gemini-2.0-flash-thinking-exp'  # Extended reasoning
        }
        
        # Configure Gemini if available
        if GENAI_AVAILABLE:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
    
    def enable_extended_thinking(self):
        """
        Enable Extended Thinking mode
        Analyzes requests more thoroughly, considers multiple approaches
        """
        self.extended_thinking_enabled = True
        logger.info("Extended Thinking enabled")
        return {
            "success": True,
            "mode": "extended_thinking",
            "features": [
                "Multi-step reasoning",
                "Edge case analysis",
                "Alternative approach consideration",
                "Deeper code analysis"
            ]
        }
    
    def enable_high_power_mode(self):
        """
        Enable High Power Mode
        Uses more advanced AI model for complex tasks
        """
        self.high_power_mode = True
        logger.info("High Power Mode enabled")
        return {
            "success": True,
            "mode": "high_power",
            "model": self.models['high_power'],
            "features": [
                "Advanced reasoning capabilities",
                "Better handling of complex tasks",
                "Improved code quality",
                "Enhanced problem-solving"
            ]
        }
    
    def get_model_for_task(self, task_complexity: str) -> str:
        """
        Select appropriate model based on task complexity
        
        Args:
            task_complexity: 'simple', 'medium', or 'complex'
        
        Returns:
            Model name
        """
        if self.high_power_mode:
            return self.models['high_power']
        
        if task_complexity == 'complex' or self.extended_thinking_enabled:
            return self.models['extended']
        
        return self.models['standard']
    
    async def analyze_with_extended_thinking(self, 
                                            prompt: str,
                                            context: Dict | None = None) -> Dict:
        """
        Analyze a prompt with extended thinking
        
        Args:
            prompt: User prompt
            context: Additional context
        
        Returns:
            Analysis results with reasoning steps
        """
        if not GENAI_AVAILABLE:
            return {
                "success": False,
                "error": "Google Generative AI not available. Install with: pip install google-generativeai",
                "fallback": "Extended thinking requires google-generativeai package"
            }
        
        try:
            context = context or {}
            
            # Enhanced prompt for extended thinking
            enhanced_prompt = f"""
Analyze this request with extended thinking:

User Request: {prompt}

Please provide:
1. Initial understanding of the request
2. Multiple possible approaches
3. Edge cases to consider
4. Potential challenges
5. Recommended solution with reasoning
6. Alternative solutions

Context: {context}

Think step-by-step and consider all aspects thoroughly.
"""
            
            model = genai.GenerativeModel(self.models['extended'])
            response = await model.generate_content_async(enhanced_prompt)
            
            return {
                "success": True,
                "analysis": response.text,
                "model": self.models['extended'],
                "mode": "extended_thinking",
                "reasoning_steps": self._extract_reasoning_steps(response.text)
            }
            
        except Exception as e:
            logger.error(f"Extended thinking analysis failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _extract_reasoning_steps(self, analysis: str) -> List[str]:
        """Extract reasoning steps from analysis"""
        steps = []
        lines = analysis.split('\n')
        
        for line in lines:
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.')):
                steps.append(line.strip())
        
        return steps if steps else ["Analysis completed"]
    
    async def generate_with_high_power(self,
                                      prompt: str,
                                      task_type: str) -> Dict:
        """
        Generate code/content with high power model
        
        Args:
            prompt: Generation prompt
            task_type: Type of task
        
        Returns:
            Generated content
        """
        if not GENAI_AVAILABLE:
            return {
                "success": False,
                "error": "Google Generative AI not available. Install with: pip install google-generativeai",
                "fallback": "High power mode requires google-generativeai package"
            }
        
        try:
            model_name = self.models['high_power']
            logger.info(f"Using High Power model: {model_name}")
            
            model = genai.GenerativeModel(model_name)
            response = await model.generate_content_async(prompt)
            
            return {
                "success": True,
                "content": response.text,
                "model": model_name,
                "mode": "high_power",
                "task_type": task_type
            }
            
        except Exception as e:
            logger.error(f"High power generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def assess_task_complexity(self, description: str) -> str:
        """
        Assess task complexity to select appropriate model
        
        Args:
            description: Task description
        
        Returns:
            Complexity level: 'simple', 'medium', or 'complex'
        """
        description_lower = description.lower()
        
        # Complex indicators
        complex_keywords = [
            'architecture', 'system design', 'optimize', 'refactor',
            'security', 'authentication', 'database schema', 'api design',
            'microservices', 'distributed', 'scalable'
        ]
        
        # Simple indicators
        simple_keywords = [
            'button', 'color', 'text', 'style', 'simple', 'basic',
            'hello world', 'example', 'demo'
        ]
        
        complex_count = sum(1 for kw in complex_keywords if kw in description_lower)
        simple_count = sum(1 for kw in simple_keywords if kw in description_lower)
        
        if complex_count >= 2:
            return 'complex'
        elif simple_count >= 2:
            return 'simple'
        else:
            return 'medium'
    
    def get_current_config(self) -> Dict:
        """Get current intelligence configuration"""
        return {
            "extended_thinking": self.extended_thinking_enabled,
            "high_power_mode": self.high_power_mode,
            "current_model": self.get_model_for_task('medium'),
            "available_models": self.models
        }


# Global instance
dynamic_intelligence = DynamicIntelligence()


def enable_extended_thinking() -> Dict:
    """Enable Extended Thinking mode"""
    return dynamic_intelligence.enable_extended_thinking()


def enable_high_power_mode() -> Dict:
    """Enable High Power Mode"""
    return dynamic_intelligence.enable_high_power_mode()


def get_smart_model(task_description: str) -> str:
    """Get the best model for a task based on complexity"""
    complexity = dynamic_intelligence.assess_task_complexity(task_description)
    return dynamic_intelligence.get_model_for_task(complexity)
