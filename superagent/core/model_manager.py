"""Model version management for SuperAgent."""

from typing import Dict, Any, Optional, List
from enum import Enum
import structlog

logger = structlog.get_logger()


class ClaudeModel(Enum):
    """Available Claude models."""
    
    # Claude 4.5 Family (Latest - September 2025)
    CLAUDE_4_5_SONNET = "claude-sonnet-4-5-20250929"
    
    # Claude 3.5 Family
    CLAUDE_3_5_SONNET_LATEST = "claude-3-5-sonnet-20241022"
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20240620"
    
    # Claude 3 Opus (Most capable)
    CLAUDE_3_OPUS_LATEST = "claude-3-opus-20240229"
    
    # Claude 3 Sonnet (Balanced)
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    
    # Claude 3 Haiku (Fastest)
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    
    # Aliases for easy access
    LATEST = "claude-sonnet-4-5-20250929"
    FASTEST = "claude-3-haiku-20240307"
    SMARTEST = "claude-sonnet-4-5-20250929"
    BALANCED = "claude-sonnet-4-5-20250929"


class ModelCapabilities:
    """Model capabilities and specifications."""
    
    MODELS = {
        "claude-sonnet-4-5-20250929": {
            "name": "Claude Sonnet 4.5 (Latest)",
            "description": "Most advanced model - best for coding and autonomous work",
            "context_window": 200000,
            "max_output": 8192,
            "cost_per_mtok_input": 3.00,
            "cost_per_mtok_output": 15.00,
            "capabilities": {
                "coding": "outstanding",
                "reasoning": "outstanding",
                "speed": "fast",
                "vision": True,
                "autonomous_hours": 30
            },
            "recommended_for": [
                "code_generation",
                "debugging",
                "refactoring",
                "code_review",
                "architecture_design",
                "autonomous_work"
            ]
        },
        "claude-3-5-sonnet-20241022": {
            "name": "Claude 3.5 Sonnet (October 2024)",
            "description": "Previous generation - still excellent for coding",
            "context_window": 200000,
            "max_output": 8192,
            "cost_per_mtok_input": 3.00,
            "cost_per_mtok_output": 15.00,
            "capabilities": {
                "coding": "excellent",
                "reasoning": "excellent", 
                "speed": "fast",
                "vision": True
            },
            "recommended_for": [
                "code_generation",
                "debugging",
                "refactoring",
                "code_review",
                "architecture_design"
            ]
        },
        "claude-3-opus-20240229": {
            "name": "Claude 3 Opus",
            "description": "Most capable model - highest intelligence",
            "context_window": 200000,
            "max_output": 4096,
            "cost_per_mtok_input": 15.00,
            "cost_per_mtok_output": 75.00,
            "capabilities": {
                "coding": "excellent",
                "reasoning": "outstanding",
                "speed": "moderate",
                "vision": True
            },
            "recommended_for": [
                "complex_problems",
                "architecture_design",
                "advanced_debugging",
                "optimization"
            ]
        },
        "claude-3-5-sonnet-20240620": {
            "name": "Claude 3.5 Sonnet",
            "description": "Balanced model - great performance",
            "context_window": 200000,
            "max_output": 8192,
            "cost_per_mtok_input": 3.00,
            "cost_per_mtok_output": 15.00,
            "capabilities": {
                "coding": "excellent",
                "reasoning": "excellent",
                "speed": "fast",
                "vision": True
            },
            "recommended_for": [
                "general_coding",
                "documentation",
                "testing"
            ]
        },
        "claude-3-sonnet-20240229": {
            "name": "Claude 3 Sonnet",
            "description": "Balanced model - good for most tasks",
            "context_window": 200000,
            "max_output": 4096,
            "cost_per_mtok_input": 3.00,
            "cost_per_mtok_output": 15.00,
            "capabilities": {
                "coding": "very_good",
                "reasoning": "very_good",
                "speed": "fast",
                "vision": True
            },
            "recommended_for": [
                "general_coding",
                "documentation",
                "simple_tasks"
            ]
        },
        "claude-3-haiku-20240307": {
            "name": "Claude 3 Haiku",
            "description": "Fastest model - quick responses",
            "context_window": 200000,
            "max_output": 4096,
            "cost_per_mtok_input": 0.25,
            "cost_per_mtok_output": 1.25,
            "capabilities": {
                "coding": "good",
                "reasoning": "good",
                "speed": "very_fast",
                "vision": True
            },
            "recommended_for": [
                "simple_tasks",
                "quick_fixes",
                "formatting",
                "linting"
            ]
        }
    }
    
    @classmethod
    def get_model_info(cls, model_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a model.
        
        Args:
            model_name: Model identifier
            
        Returns:
            Model information dictionary
        """
        return cls.MODELS.get(model_name)
    
    @classmethod
    def get_recommended_model(cls, task_type: str) -> str:
        """Get recommended model for a task type.
        
        Args:
            task_type: Type of task
            
        Returns:
            Recommended model name
        """
        task_map = {
            "code_generation": ClaudeModel.CLAUDE_4_5_SONNET.value,
            "debugging": ClaudeModel.CLAUDE_4_5_SONNET.value,
            "refactoring": ClaudeModel.CLAUDE_4_5_SONNET.value,
            "code_review": ClaudeModel.CLAUDE_4_5_SONNET.value,
            "documentation": ClaudeModel.CLAUDE_4_5_SONNET.value,
            "autonomous_work": ClaudeModel.CLAUDE_4_5_SONNET.value,
            "testing": ClaudeModel.CLAUDE_4_5_SONNET.value,
            "simple_task": ClaudeModel.CLAUDE_3_HAIKU.value,
            "complex_problem": ClaudeModel.CLAUDE_4_5_SONNET.value,
            "architecture": ClaudeModel.CLAUDE_4_5_SONNET.value,
        }
        
        return task_map.get(task_type, ClaudeModel.LATEST.value)
    
    @classmethod
    def list_models(cls) -> List[Dict[str, Any]]:
        """List all available models.
        
        Returns:
            List of model information
        """
        return [
            {
                "id": model_id,
                **info
            }
            for model_id, info in cls.MODELS.items()
        ]
    
    @classmethod
    def compare_models(cls, model1: str, model2: str) -> Dict[str, Any]:
        """Compare two models.
        
        Args:
            model1: First model
            model2: Second model
            
        Returns:
            Comparison data
        """
        info1 = cls.get_model_info(model1)
        info2 = cls.get_model_info(model2)
        
        if not info1 or not info2:
            return {"error": "Model not found"}
        
        return {
            "model1": {
                "name": info1["name"],
                "context": info1["context_window"],
                "cost_input": info1["cost_per_mtok_input"],
                "cost_output": info1["cost_per_mtok_output"],
                "speed": info1["capabilities"]["speed"]
            },
            "model2": {
                "name": info2["name"],
                "context": info2["context_window"],
                "cost_input": info2["cost_per_mtok_input"],
                "cost_output": info2["cost_per_mtok_output"],
                "speed": info2["capabilities"]["speed"]
            },
            "recommendation": cls._get_comparison_recommendation(info1, info2)
        }
    
    @classmethod
    def _get_comparison_recommendation(cls, info1: Dict, info2: Dict) -> str:
        """Get recommendation between two models."""
        cost1 = info1["cost_per_mtok_input"] + info1["cost_per_mtok_output"]
        cost2 = info2["cost_per_mtok_input"] + info2["cost_per_mtok_output"]
        
        if cost1 < cost2:
            return f"{info1['name']} is more cost-effective"
        elif cost1 > cost2:
            return f"{info2['name']} is more cost-effective"
        else:
            return "Models have similar pricing"


class ModelManager:
    """Manages model selection and switching."""
    
    def __init__(self, default_model: Optional[str] = None):
        """Initialize model manager.
        
        Args:
            default_model: Default model to use
        """
        self.current_model = default_model or ClaudeModel.LATEST.value
        self.model_history: List[Dict[str, Any]] = []
    
    def set_model(self, model_name: str) -> bool:
        """Set the current model.
        
        Args:
            model_name: Model to switch to
            
        Returns:
            True if successful
        """
        # Check if model exists
        if model_name in ClaudeModel.__members__:
            model_name = ClaudeModel[model_name].value
        
        info = ModelCapabilities.get_model_info(model_name)
        
        if not info:
            logger.error(f"Unknown model: {model_name}")
            return False
        
        old_model = self.current_model
        self.current_model = model_name
        
        self.model_history.append({
            "from": old_model,
            "to": model_name,
            "reason": "manual_switch"
        })
        
        logger.info(f"Switched model: {old_model} → {model_name}")
        return True
    
    def get_model_for_task(self, task_type: str) -> str:
        """Get optimal model for a task.
        
        Args:
            task_type: Type of task
            
        Returns:
            Model name
        """
        return ModelCapabilities.get_recommended_model(task_type)
    
    def auto_select_model(self, 
                         task_type: str,
                         context_size: Optional[int] = None,
                         prioritize_speed: bool = False,
                         prioritize_cost: bool = False) -> str:
        """Automatically select best model for requirements.
        
        Args:
            task_type: Type of task
            context_size: Required context window size
            prioritize_speed: Prioritize speed over quality
            prioritize_cost: Prioritize cost over quality
            
        Returns:
            Selected model name
        """
        candidates = []
        
        for model_id, info in ModelCapabilities.MODELS.items():
            # Check context window requirement
            if context_size and info["context_window"] < context_size:
                continue
            
            # Check if suitable for task
            if task_type in info["recommended_for"]:
                candidates.append((model_id, info))
        
        if not candidates:
            # Fallback to default
            return ClaudeModel.LATEST.value
        
        # Sort based on priorities
        if prioritize_speed:
            # Sort by speed
            speed_order = {"very_fast": 0, "fast": 1, "moderate": 2}
            candidates.sort(
                key=lambda x: speed_order.get(x[1]["capabilities"]["speed"], 3)
            )
        elif prioritize_cost:
            # Sort by cost
            candidates.sort(
                key=lambda x: x[1]["cost_per_mtok_input"] + x[1]["cost_per_mtok_output"]
            )
        else:
            # Prioritize quality (use latest/best)
            if any(m[0] == ClaudeModel.LATEST.value for m in candidates):
                return ClaudeModel.LATEST.value
        
        selected = candidates[0][0]
        logger.info(f"Auto-selected model: {selected} for task: {task_type}")
        
        return selected
    
    def get_current_model_info(self) -> Dict[str, Any]:
        """Get information about current model.
        
        Returns:
            Model information
        """
        info = ModelCapabilities.get_model_info(self.current_model)
        return {
            "current_model": self.current_model,
            "info": info,
            "switches": len(self.model_history)
        }
    
    def estimate_cost(self, input_tokens: int, output_tokens: int,
                     model: Optional[str] = None) -> Dict[str, float]:
        """Estimate cost for token usage.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model to estimate for (default: current)
            
        Returns:
            Cost estimate
        """
        model = model or self.current_model
        info = ModelCapabilities.get_model_info(model)
        
        if not info:
            return {"error": "Unknown model"}
        
        input_cost = (input_tokens / 1_000_000) * info["cost_per_mtok_input"]
        output_cost = (output_tokens / 1_000_000) * info["cost_per_mtok_output"]
        
        return {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": input_cost + output_cost
        }

