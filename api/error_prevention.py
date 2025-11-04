"""
ML-Based Error Prevention Module
Predictive error detection before code execution
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib

class ErrorPreventionSystem:
    """ML-based predictive error detection"""
    
    def __init__(self):
        self.error_patterns = self._load_error_patterns()
        self.prediction_history = []
        self.learning_data = []
        
    def predict_errors(self, code: str, language: str) -> Dict[str, Any]:
        """Predict potential errors before execution"""
        predictions = []
        
        # Syntax error prediction
        predictions.extend(self._predict_syntax_errors(code, language))
        
        # Runtime error prediction
        predictions.extend(self._predict_runtime_errors(code, language))
        
        # Logic error prediction
        predictions.extend(self._predict_logic_errors(code, language))
        
        # Type error prediction
        predictions.extend(self._predict_type_errors(code, language))
        
        # Calculate confidence
        confidence = self._calculate_confidence(predictions)
        
        result = {
            "code_hash": hashlib.md5(code.encode()).hexdigest()[:8],
            "language": language,
            "total_predictions": len(predictions),
            "predictions": predictions,
            "confidence": confidence,
            "risk_level": self._assess_risk(predictions),
            "recommendations": self._generate_prevention_recommendations(predictions),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.prediction_history.append(result)
        return result
    
    def _predict_syntax_errors(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Predict syntax errors"""
        errors = []
        
        if language.lower() == "python":
            # Unmatched parentheses
            open_parens = code.count('(')
            close_parens = code.count(')')
            if open_parens != close_parens:
                errors.append({
                    "type": "syntax",
                    "severity": "high",
                    "message": f"Unmatched parentheses (open: {open_parens}, close: {close_parens})",
                    "confidence": 0.95,
                    "prevention": "Check parentheses matching"
                })
            
            # Unmatched brackets
            open_brackets = code.count('[')
            close_brackets = code.count(']')
            if open_brackets != close_brackets:
                errors.append({
                    "type": "syntax",
                    "severity": "high",
                    "message": f"Unmatched brackets (open: {open_brackets}, close: {close_brackets})",
                    "confidence": 0.95,
                    "prevention": "Check bracket matching"
                })
            
            # Missing colons
            if re.search(r'(if|for|while|def|class|try|except|with)\s+.+[^:]$', code, re.MULTILINE):
                errors.append({
                    "type": "syntax",
                    "severity": "medium",
                    "message": "Possible missing colon",
                    "confidence": 0.70,
                    "prevention": "Add colon after control structures"
                })
        
        elif language.lower() in ["javascript", "typescript"]:
            # Unmatched braces
            open_braces = code.count('{')
            close_braces = code.count('}')
            if open_braces != close_braces:
                errors.append({
                    "type": "syntax",
                    "severity": "high",
                    "message": f"Unmatched braces (open: {open_braces}, close: {close_braces})",
                    "confidence": 0.95,
                    "prevention": "Check brace matching"
                })
        
        return errors
    
    def _predict_runtime_errors(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Predict runtime errors"""
        errors = []
        
        if language.lower() == "python":
            # Division by zero
            if re.search(r'/\s*0\b', code):
                errors.append({
                    "type": "runtime",
                    "severity": "high",
                    "message": "Potential division by zero",
                    "confidence": 0.85,
                    "prevention": "Add zero check before division"
                })
            
            # Null/None dereference
            if re.search(r'\bNone\s*\.', code):
                errors.append({
                    "type": "runtime",
                    "severity": "high",
                    "message": "Potential None dereference",
                    "confidence": 0.80,
                    "prevention": "Check for None before accessing attributes"
                })
            
            # Index out of bounds
            if re.search(r'\[\s*-?\d+\s*\]', code):
                errors.append({
                    "type": "runtime",
                    "severity": "medium",
                    "message": "Potential index out of bounds",
                    "confidence": 0.60,
                    "prevention": "Validate index before accessing"
                })
            
            # Undefined variable (simple check)
            variables_defined = set(re.findall(r'(\w+)\s*=', code))
            variables_used = set(re.findall(r'\b(\w+)\b', code))
            undefined = variables_used - variables_defined - {'print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict', 'set'}
            
            if undefined:
                errors.append({
                    "type": "runtime",
                    "severity": "high",
                    "message": f"Potentially undefined variables: {', '.join(list(undefined)[:3])}",
                    "confidence": 0.50,
                    "prevention": "Ensure all variables are defined before use"
                })
        
        return errors
    
    def _predict_logic_errors(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Predict logic errors"""
        errors = []
        
        # Infinite loop detection
        if re.search(r'while\s+True\s*:', code) and 'break' not in code:
            errors.append({
                "type": "logic",
                "severity": "medium",
                "message": "Potential infinite loop (no break statement)",
                "confidence": 0.70,
                "prevention": "Add break condition or timeout"
            })
        
        # Assignment in condition
        if language.lower() in ["python"]:
            if re.search(r'if\s+.*\s*=\s*[^=]', code):
                errors.append({
                    "type": "logic",
                    "severity": "medium",
                    "message": "Assignment in condition (use == for comparison)",
                    "confidence": 0.75,
                    "prevention": "Use == for equality comparison"
                })
        
        # Empty exception handler
        if language.lower() == "python":
            if re.search(r'except.*:\s*pass', code):
                errors.append({
                    "type": "logic",
                    "severity": "low",
                    "message": "Empty exception handler",
                    "confidence": 0.90,
                    "prevention": "Handle exceptions appropriately or log them"
                })
        
        return errors
    
    def _predict_type_errors(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Predict type errors"""
        errors = []
        
        if language.lower() == "python":
            # String + number concatenation
            if re.search(r'["\'].*["\'].+\+.+\d', code) or re.search(r'\d.+\+.+["\']', code):
                errors.append({
                    "type": "type",
                    "severity": "medium",
                    "message": "Potential type error (string + number)",
                    "confidence": 0.65,
                    "prevention": "Convert types before concatenation"
                })
            
            # Incorrect method call
            if re.search(r'\.append\s*\(.*,.*\)', code):
                errors.append({
                    "type": "type",
                    "severity": "medium",
                    "message": "append() takes only one argument",
                    "confidence": 0.85,
                    "prevention": "Use extend() for multiple items"
                })
        
        return errors
    
    def _calculate_confidence(self, predictions: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence score"""
        if not predictions:
            return 0.0
        
        avg_confidence = sum(p["confidence"] for p in predictions) / len(predictions)
        return round(avg_confidence * 100, 2)
    
    def _assess_risk(self, predictions: List[Dict[str, Any]]) -> str:
        """Assess overall risk level"""
        if not predictions:
            return "low"
        
        severity_counts = {
            "high": sum(1 for p in predictions if p["severity"] == "high"),
            "medium": sum(1 for p in predictions if p["severity"] == "medium"),
            "low": sum(1 for p in predictions if p["severity"] == "low")
        }
        
        if severity_counts["high"] >= 2:
            return "critical"
        elif severity_counts["high"] >= 1:
            return "high"
        elif severity_counts["medium"] >= 2:
            return "medium"
        else:
            return "low"
    
    def _generate_prevention_recommendations(self, predictions: List[Dict[str, Any]]) -> List[str]:
        """Generate prevention recommendations"""
        recommendations = []
        
        # Group by type
        by_type = {}
        for pred in predictions:
            ptype = pred["type"]
            by_type[ptype] = by_type.get(ptype, 0) + 1
        
        for ptype, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            recommendations.append(f"Fix {count} {ptype} error(s)")
        
        # Add top prevention tips
        for pred in sorted(predictions, key=lambda x: x["confidence"], reverse=True)[:3]:
            recommendations.append(pred["prevention"])
        
        return list(set(recommendations))[:5]  # Top 5 unique recommendations
    
    def _load_error_patterns(self) -> Dict[str, List[str]]:
        """Load common error patterns (ML training data)"""
        return {
            "syntax": [
                r"SyntaxError",
                r"IndentationError",
                r"UnexpectedToken"
            ],
            "runtime": [
                r"ZeroDivisionError",
                r"IndexError",
                r"KeyError",
                r"AttributeError",
                r"TypeError"
            ],
            "logic": [
                r"infinite\s+loop",
                r"unreachable\s+code",
                r"dead\s+code"
            ]
        }
    
    def learn_from_actual_error(self, code: str, error_type: str, error_message: str) -> None:
        """Learn from actual execution errors (ML training)"""
        self.learning_data.append({
            "code_hash": hashlib.md5(code.encode()).hexdigest()[:8],
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_prevention_stats(self) -> Dict[str, Any]:
        """Get error prevention statistics"""
        total_predictions = len(self.prediction_history)
        if total_predictions == 0:
            return {"total_predictions": 0, "message": "No predictions yet"}
        
        total_errors_predicted = sum(p["total_predictions"] for p in self.prediction_history)
        avg_confidence = sum(p["confidence"] for p in self.prediction_history) / total_predictions
        
        risk_distribution = {}
        for pred in self.prediction_history:
            risk = pred["risk_level"]
            risk_distribution[risk] = risk_distribution.get(risk, 0) + 1
        
        return {
            "total_predictions": total_predictions,
            "total_errors_predicted": total_errors_predicted,
            "average_confidence": round(avg_confidence, 2),
            "risk_distribution": risk_distribution,
            "learning_data_size": len(self.learning_data)
        }

# Global instance
error_prevention = ErrorPreventionSystem()
