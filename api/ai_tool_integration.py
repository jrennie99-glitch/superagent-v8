"""
AI Model Integration with Tool Calling
Enables Gemini, Claude, GPT, and Groq models to use SuperAgent tools
"""

import os
import json
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from .tools_system import registry

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

class AIToolAgent:
    """AI Agent with tool-calling capabilities"""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        self.model_name = model_name
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Get tool definitions
        self.tools = registry.get_tool_definitions()
        
        # Configure model with tools
        self.model = genai.GenerativeModel(
            model_name=model_name,
            tools=self._convert_tools_to_gemini_format()
        )
        
        self.conversation_history = []
    
    def _convert_tools_to_gemini_format(self) -> List[Dict]:
        """Convert tool definitions to Gemini function calling format"""
        gemini_tools = []
        
        for tool in self.tools:
            gemini_tools.append({
                "function_declarations": [{
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }]
            })
        
        return gemini_tools
    
    async def chat(self, user_message: str, auto_execute: bool = True) -> Dict[str, Any]:
        """
        Chat with AI that can use tools
        
        Args:
            user_message: User's message
            auto_execute: Whether to automatically execute tool calls
        
        Returns:
            Response with text and tool execution results
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "parts": [user_message]
        })
        
        # Start chat with history
        chat = self.model.start_chat(history=self.conversation_history[:-1])
        
        # Send message
        response = chat.send_message(user_message)
        
        # Check for function calls
        tool_calls = []
        final_response = ""
        
        for part in response.parts:
            # Check if this part is a function call
            if hasattr(part, 'function_call') and part.function_call:
                function_call = part.function_call
                
                tool_call_info = {
                    "name": function_call.name,
                    "arguments": dict(function_call.args),
                    "executed": False,
                    "result": None
                }
                
                # Auto-execute if enabled
                if auto_execute:
                    try:
                        result = await registry.execute_tool(
                            function_call.name,
                            dict(function_call.args)
                        )
                        tool_call_info["executed"] = True
                        tool_call_info["result"] = result
                        
                        # Send result back to model
                        function_response = chat.send_message({
                            "function_response": {
                                "name": function_call.name,
                                "response": {"result": str(result)}
                            }
                        })
                        
                        # Get final text response
                        if function_response.text:
                            final_response = function_response.text
                    
                    except Exception as e:
                        tool_call_info["result"] = f"Error: {str(e)}"
                
                tool_calls.append(tool_call_info)
            
            # Get text response
            elif hasattr(part, 'text') and part.text:
                final_response = part.text
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "model",
            "parts": [final_response] if final_response else []
        })
        
        return {
            "response": final_response,
            "tool_calls": tool_calls,
            "model": self.model_name
        }
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return [tool["name"] for tool in self.tools]


class GroqAgent:
    """Lightning-fast AI Agent using Groq inference"""
    
    def __init__(self, model_name: str = "llama-3.1-70b-versatile"):
        self.model_name = model_name
        self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY')) if GROQ_AVAILABLE else None
        self.conversation_history = []
    
    async def chat(self, user_message: str, auto_execute: bool = True) -> Dict[str, Any]:
        """
        Lightning-fast chat using Groq
        
        Args:
            user_message: User's message
            auto_execute: Whether to automatically execute tool calls
        
        Returns:
            Response with text
        """
        if not self.groq_client:
            return {
                "response": "Groq is not available. Install with: pip install groq",
                "model": "error"
            }
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            # Call Groq API
            response = self.groq_client.chat.completions.create(
                model=self.model_name,
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=4096
            )
            
            assistant_message = response.choices[0].message.content
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return {
                "response": assistant_message,
                "tool_calls": [],
                "model": f"groq/{self.model_name}"
            }
        
        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "tool_calls": [],
                "model": "error"
            }
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []


class MultiModelRouter:
    """
    Intelligent routing between AI models based on task type
    """
    
    def __init__(self):
        # Initialize Groq agent if available
        groq_agent = None
        if GROQ_AVAILABLE and os.getenv('GROQ_API_KEY'):
            groq_agent = GroqAgent("llama-3.1-70b-versatile")
        
        self.agents = {
            "code": AIToolAgent("gemini-2.0-flash-exp"),  # Best for code
            "reasoning": None,  # Claude Sonnet (if API key available)
            "writing": None,  # GPT-4 (if API key available)
            "groq": groq_agent,  # Lightning-fast Groq
            "fast": groq_agent,  # Alias for Groq (fast mode)
        }
    
    async def route_and_execute(self, task: str, task_type: str = "auto") -> Dict[str, Any]:
        """
        Route task to best model and execute
        
        Args:
            task: Task description
            task_type: Type of task (code, reasoning, writing, auto)
        
        Returns:
            Response from appropriate model
        """
        # Auto-detect task type if not specified
        if task_type == "auto":
            task_type = self._detect_task_type(task)
        
        # Route to appropriate agent
        agent = self.agents.get(task_type, self.agents["code"])
        
        if agent is None:
            # Fallback to code agent if specialized agent not available
            agent = self.agents["code"]
        
        return await agent.chat(task)
    
    def _detect_task_type(self, task: str) -> str:
        """Auto-detect task type from content"""
        task_lower = task.lower()
        
        # Code-related keywords
        code_keywords = ['code', 'function', 'class', 'debug', 'implement', 'refactor', 'api', 'database']
        if any(keyword in task_lower for keyword in code_keywords):
            return "code"
        
        # Reasoning keywords
        reasoning_keywords = ['analyze', 'explain', 'why', 'how', 'think', 'reason', 'logic']
        if any(keyword in task_lower for keyword in reasoning_keywords):
            return "reasoning"
        
        # Writing keywords
        writing_keywords = ['write', 'compose', 'draft', 'documentation', 'readme', 'blog']
        if any(keyword in task_lower for keyword in writing_keywords):
            return "writing"
        
        # Default to code
        return "code"
