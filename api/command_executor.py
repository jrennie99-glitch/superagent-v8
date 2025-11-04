"""
Command Executor Module - Run shell commands safely
"""
import subprocess
import asyncio
from typing import Dict

class CommandExecutor:
    """Execute shell commands with output capture"""
    
    def __init__(self):
        self.timeout = 60
        self.blocked_commands = ['rm -rf /', 'shutdown', 'reboot', 'mkfs']
    
    async def execute_command(self, command: str, timeout: int = None) -> Dict:
        """Execute a shell command and return output"""
        try:
            if timeout is None:
                timeout = self.timeout
            
            if any(blocked in command for blocked in self.blocked_commands):
                return {
                    "success": False,
                    "error": "Command blocked for safety",
                    "command": command
                }
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                return {
                    "success": process.returncode == 0,
                    "command": command,
                    "stdout": stdout.decode('utf-8', errors='ignore'),
                    "stderr": stderr.decode('utf-8', errors='ignore'),
                    "exit_code": process.returncode
                }
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "error": f"Command timeout after {timeout}s",
                    "command": command
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
