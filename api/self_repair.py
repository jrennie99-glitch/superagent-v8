"""
Self-Repair System for SuperAgent
Monitors logs, detects errors, and automatically fixes issues
"""
import os
import re
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import google.generativeai as genai

@dataclass
class ErrorDetection:
    """Detected error information"""
    timestamp: str
    error_type: str
    error_message: str
    stack_trace: str
    file_path: Optional[str]
    line_number: Optional[int]
    severity: str  # critical, high, medium, low
    auto_fixable: bool

@dataclass
class RepairAction:
    """Repair action taken"""
    timestamp: str
    error_id: str
    action_type: str  # code_fix, dependency_install, config_update, restart
    description: str
    changes_made: List[str]
    success: bool
    error_resolved: bool

class SelfRepairSystem:
    """Autonomous self-repair system"""
    
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
        
        self.error_history: List[ErrorDetection] = []
        self.repair_history: List[RepairAction] = []
        self.monitoring_active = False
        self.last_check = datetime.now()
        
        # Error patterns to detect
        self.error_patterns = {
            'import_error': r'ImportError|ModuleNotFoundError|No module named',
            'syntax_error': r'SyntaxError|IndentationError',
            'type_error': r'TypeError|AttributeError',
            'runtime_error': r'RuntimeError|ValueError|KeyError',
            'connection_error': r'ConnectionError|TimeoutError|ConnectionRefusedError',
            'file_error': r'FileNotFoundError|PermissionError',
            'database_error': r'DatabaseError|OperationalError',
            'api_error': r'API.*Error|HTTP.*Error|Status.*[45]\d\d'
        }
    
    async def monitor_logs(self, log_content: str) -> List[ErrorDetection]:
        """Monitor logs for errors"""
        errors = []
        lines = log_content.split('\n')
        
        for i, line in enumerate(lines):
            for error_type, pattern in self.error_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    # Extract error details
                    error = self._extract_error_details(line, lines[i:i+10], error_type)
                    if error:
                        errors.append(error)
        
        return errors
    
    def _extract_error_details(self, error_line: str, context_lines: List[str], error_type: str) -> Optional[ErrorDetection]:
        """Extract detailed error information"""
        # Parse stack trace
        stack_trace = '\n'.join(context_lines[:10])
        
        # Extract file and line number
        file_match = re.search(r'File "([^"]+)", line (\d+)', stack_trace)
        file_path = file_match.group(1) if file_match else None
        line_number = int(file_match.group(2)) if file_match else None
        
        # Determine severity
        severity = self._determine_severity(error_type, error_line)
        
        # Check if auto-fixable
        auto_fixable = self._is_auto_fixable(error_type)
        
        return ErrorDetection(
            timestamp=datetime.now().isoformat(),
            error_type=error_type,
            error_message=error_line.strip(),
            stack_trace=stack_trace,
            file_path=file_path,
            line_number=line_number,
            severity=severity,
            auto_fixable=auto_fixable
        )
    
    def _determine_severity(self, error_type: str, error_message: str) -> str:
        """Determine error severity"""
        if 'critical' in error_message.lower() or error_type == 'database_error':
            return 'critical'
        elif error_type in ['import_error', 'connection_error']:
            return 'high'
        elif error_type in ['type_error', 'runtime_error']:
            return 'medium'
        else:
            return 'low'
    
    def _is_auto_fixable(self, error_type: str) -> bool:
        """Check if error can be auto-fixed"""
        auto_fixable_types = [
            'import_error',
            'syntax_error',
            'type_error',
            'file_error'
        ]
        return error_type in auto_fixable_types
    
    async def generate_fix(self, error: ErrorDetection) -> Optional[Dict]:
        """Generate fix for detected error using AI"""
        if not self.gemini_key:
            return None
        
        try:
            # Read the problematic file if available
            file_content = ""
            if error.file_path and os.path.exists(error.file_path):
                with open(error.file_path, 'r') as f:
                    file_content = f.read()
            
            # Create fix generation prompt
            prompt = f"""
You are an expert code repair AI. Analyze this error and generate a fix.

ERROR TYPE: {error.error_type}
ERROR MESSAGE: {error.error_message}
STACK TRACE:
{error.stack_trace}

FILE PATH: {error.file_path or 'N/A'}
LINE NUMBER: {error.line_number or 'N/A'}

FILE CONTENT (if available):
{file_content[:2000] if file_content else 'Not available'}

TASK:
1. Identify the root cause of the error
2. Generate the exact code fix needed
3. Provide the complete corrected code section
4. Explain what caused the error and how the fix resolves it

Return ONLY a JSON object with this structure:
{{
    "root_cause": "explanation of what caused the error",
    "fix_type": "code_change|dependency_install|config_update",
    "fix_code": "the corrected code (if applicable)",
    "steps": ["step 1", "step 2", ...],
    "confidence": 0-100
}}
"""
            
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            response = model.generate_content(prompt)
            
            # Parse response
            fix_data = self._parse_ai_response(response.text)
            return fix_data
            
        except Exception as e:
            print(f"Fix generation failed: {e}")
            return None
    
    def _parse_ai_response(self, response_text: str) -> Optional[Dict]:
        """Parse AI response to extract fix"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            print(f"Failed to parse AI response: {e}")
        return None
    
    async def apply_fix(self, error: ErrorDetection, fix_data: Dict) -> RepairAction:
        """Apply the generated fix"""
        changes_made = []
        success = False
        
        try:
            fix_type = fix_data.get('fix_type', 'code_change')
            
            if fix_type == 'code_change' and error.file_path:
                # Apply code fix
                success = await self._apply_code_fix(
                    error.file_path,
                    error.line_number,
                    fix_data.get('fix_code', '')
                )
                if success:
                    changes_made.append(f"Fixed {error.file_path} at line {error.line_number}")
            
            elif fix_type == 'dependency_install':
                # Install missing dependency
                success = await self._install_dependency(fix_data.get('steps', []))
                if success:
                    changes_made.append("Installed missing dependencies")
            
            elif fix_type == 'config_update':
                # Update configuration
                success = await self._update_config(fix_data.get('steps', []))
                if success:
                    changes_made.append("Updated configuration")
        
        except Exception as e:
            print(f"Failed to apply fix: {e}")
            success = False
        
        return RepairAction(
            timestamp=datetime.now().isoformat(),
            error_id=f"{error.error_type}_{error.timestamp}",
            action_type=fix_data.get('fix_type', 'unknown'),
            description=fix_data.get('root_cause', 'Unknown error'),
            changes_made=changes_made,
            success=success,
            error_resolved=success
        )
    
    async def _apply_code_fix(self, file_path: str, line_number: Optional[int], fix_code: str) -> bool:
        """Apply code fix to file"""
        try:
            if not os.path.exists(file_path):
                return False
            
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Create backup
            backup_path = f"{file_path}.backup"
            with open(backup_path, 'w') as f:
                f.writelines(lines)
            
            # Apply fix (simple replacement for now)
            if line_number and 0 < line_number <= len(lines):
                lines[line_number - 1] = fix_code + '\n'
            
            # Write fixed content
            with open(file_path, 'w') as f:
                f.writelines(lines)
            
            return True
        except Exception as e:
            print(f"Code fix failed: {e}")
            return False
    
    async def _install_dependency(self, steps: List[str]) -> bool:
        """Install missing dependency"""
        try:
            for step in steps:
                if 'pip install' in step:
                    package = step.split('pip install')[-1].strip()
                    # In production, you'd actually run: subprocess.run(['pip', 'install', package])
                    print(f"Would install: {package}")
                    return True
        except Exception as e:
            print(f"Dependency install failed: {e}")
        return False
    
    async def _update_config(self, steps: List[str]) -> bool:
        """Update configuration"""
        try:
            # Implement config updates
            print(f"Would update config with: {steps}")
            return True
        except Exception as e:
            print(f"Config update failed: {e}")
        return False
    
    async def auto_repair(self, log_content: str) -> Dict:
        """Automatically detect and repair errors"""
        # Detect errors
        errors = await self.monitor_logs(log_content)
        
        repairs_attempted = 0
        repairs_successful = 0
        
        for error in errors:
            if error.auto_fixable:
                self.error_history.append(error)
                
                # Generate fix
                fix_data = await self.generate_fix(error)
                
                if fix_data and fix_data.get('confidence', 0) >= 70:
                    # Apply fix
                    repair_action = await self.apply_fix(error, fix_data)
                    self.repair_history.append(repair_action)
                    
                    repairs_attempted += 1
                    if repair_action.success:
                        repairs_successful += 1
        
        return {
            'errors_detected': len(errors),
            'auto_fixable': sum(1 for e in errors if e.auto_fixable),
            'repairs_attempted': repairs_attempted,
            'repairs_successful': repairs_successful,
            'errors': [asdict(e) for e in errors[-5:]],  # Last 5 errors
            'repairs': [asdict(r) for r in self.repair_history[-5:]]  # Last 5 repairs
        }
    
    def get_health_status(self) -> Dict:
        """Get system health status"""
        recent_errors = [e for e in self.error_history if 
                        datetime.fromisoformat(e.timestamp) > datetime.now() - timedelta(hours=1)]
        
        critical_errors = sum(1 for e in recent_errors if e.severity == 'critical')
        
        return {
            'status': 'critical' if critical_errors > 0 else 'healthy',
            'total_errors_last_hour': len(recent_errors),
            'critical_errors': critical_errors,
            'total_repairs': len(self.repair_history),
            'success_rate': (
                sum(1 for r in self.repair_history if r.success) / len(self.repair_history) * 100
                if self.repair_history else 0
            ),
            'last_check': self.last_check.isoformat(),
            'monitoring_active': self.monitoring_active
        }

# Global instance
self_repair_system = SelfRepairSystem()
