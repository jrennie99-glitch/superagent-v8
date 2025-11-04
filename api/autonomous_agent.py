"""
Autonomous Agent Controller - Full Replit Agent Intelligence
Makes SuperAgent fully autonomous with planning, execution, and error recovery
"""
import os
import google.generativeai as genai
from typing import Dict, List, Any, Optional
import json
import asyncio

class AutonomousAgent:
    """
    Fully autonomous AI agent that can:
    - Understand natural language requests
    - Plan multi-step workflows
    - Execute tasks autonomously
    - Recover from errors
    - Make intelligent decisions about which tools to use
    """
    
    def __init__(self, file_ops, command_executor, web_search, codebase_search, 
                 db_manager, env_manager, deploy_manager, project_analyzer):
        """Initialize with all available tools"""
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None
        
        # All available tools
        self.tools = {
            "file_ops": file_ops,
            "command": command_executor,
            "web_search": web_search,
            "code_search": codebase_search,
            "database": db_manager,
            "environment": env_manager,
            "deployment": deploy_manager,
            "project": project_analyzer
        }
        
        # Agent memory
        self.context = []
        self.executed_steps = []
    
    async def execute_autonomous_task(self, user_request: str) -> Dict:
        """
        Main autonomous execution loop
        1. Understand request
        2. Create plan
        3. Execute steps
        4. Handle errors
        5. Return results
        """
        if not self.model:
            return {
                "success": False,
                "error": "AI model not configured. Set GEMINI_API_KEY."
            }
        
        try:
            # Step 1: Understand the request and create a plan
            plan = await self._create_plan(user_request)
            
            if not plan["success"]:
                return plan
            
            # Step 2: Execute the plan step by step
            results = await self._execute_plan(plan["steps"])
            
            return {
                "success": True,
                "request": user_request,
                "plan": plan["steps"],
                "results": results,
                "steps_executed": len(self.executed_steps)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "request": user_request
            }
    
    async def _create_plan(self, user_request: str) -> Dict:
        """Use AI to create a step-by-step plan"""
        try:
            # Get project context
            project_info = self.tools["project"].get_project_info()
            
            prompt = f"""You are an autonomous AI agent. Create a step-by-step plan to accomplish this request:

REQUEST: {user_request}

PROJECT CONTEXT:
{json.dumps(project_info, indent=2)}

AVAILABLE TOOLS:
- file_ops: read, write, delete, search files
- command: execute shell commands
- web_search: search documentation and APIs
- code_search: find functions, classes in codebase
- database: SQL queries, table management
- environment: check secrets, env vars
- deployment: configure production deployment
- project: analyze project structure

Create a JSON plan with these fields:
{{
  "success": true,
  "steps": [
    {{
      "step": 1,
      "action": "tool_name.method",
      "description": "what this step does",
      "params": {{}},
      "critical": true/false
    }}
  ],
  "reasoning": "why this plan works"
}}

Be specific and executable. Each step must use an available tool."""

            response = self.model.generate_content(prompt)
            
            # Parse the response
            plan_text = response.text.strip()
            
            # Extract JSON from markdown code blocks if present
            if "```json" in plan_text:
                plan_text = plan_text.split("```json")[1].split("```")[0].strip()
            elif "```" in plan_text:
                plan_text = plan_text.split("```")[1].split("```")[0].strip()
            
            plan = json.loads(plan_text)
            return plan
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create plan: {str(e)}"
            }
    
    async def _execute_plan(self, steps: List[Dict]) -> List[Dict]:
        """Execute each step in the plan"""
        results = []
        
        for step in steps:
            try:
                result = await self._execute_step(step)
                results.append(result)
                self.executed_steps.append(step)
                
                # If critical step fails, stop execution
                if not result.get("success") and step.get("critical"):
                    results.append({
                        "error": "Critical step failed, stopping execution",
                        "failed_step": step
                    })
                    break
                    
            except Exception as e:
                results.append({
                    "success": False,
                    "step": step,
                    "error": str(e)
                })
                
                if step.get("critical"):
                    break
        
        return results
    
    async def _execute_step(self, step: Dict) -> Dict:
        """Execute a single step using the appropriate tool"""
        action = step.get("action", "")
        params = step.get("params", {})
        
        try:
            # Parse action (e.g., "file_ops.read_file")
            if "." in action:
                tool_name, method_name = action.split(".", 1)
            else:
                return {
                    "success": False,
                    "error": f"Invalid action format: {action}"
                }
            
            # Get the tool
            tool = self.tools.get(tool_name)
            if not tool:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }
            
            # Get the method
            method = getattr(tool, method_name, None)
            if not method:
                return {
                    "success": False,
                    "error": f"Unknown method: {method_name} on tool {tool_name}"
                }
            
            # Execute the method
            if asyncio.iscoroutinefunction(method):
                result = await method(**params)
            else:
                result = method(**params)
            
            return {
                "success": True,
                "step": step,
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "step": step,
                "error": str(e)
            }
    
    def get_agent_status(self) -> Dict:
        """Get current agent status"""
        return {
            "tools_available": list(self.tools.keys()),
            "steps_executed": len(self.executed_steps),
            "context_size": len(self.context),
            "model_configured": self.model is not None
        }
    
    def clear_context(self):
        """Clear agent memory"""
        self.context = []
        self.executed_steps = []
