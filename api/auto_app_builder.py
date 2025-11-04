"""
Auto App Builder - Autonomous app building from chat
Detects code/app requests and builds complete applications automatically
"""
import os
import re
import asyncio
from typing import Dict, Any
from pathlib import Path
import google.generativeai as genai

from .app_builder import AppBuilder


class AutoAppBuilder:
    """Automatically builds apps from user messages"""
    
    def __init__(self):
        self.app_builder = AppBuilder()
        
        # Initialize Gemini for code generation
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            self.model = None
    
    def should_build_app(self, message: str, uploaded_file: Any = None) -> bool:
        """Detect if user wants to build an app"""
        
        # Explicit build requests
        build_keywords = [
            "build this", "create this app", "make this app",
            "build app", "create app", "generate app",
            "build me", "create me", "make me"
        ]
        
        if any(keyword in message.lower() for keyword in build_keywords):
            return True
        
        # File uploaded with code
        if uploaded_file and uploaded_file.get('content'):
            content = uploaded_file['content']
            # Check if it's code (contains common code patterns)
            code_indicators = ['import ', 'from ', 'def ', 'class ', 'function ', '<html', '<!DOCTYPE']
            if any(indicator in content for indicator in code_indicators):
                return True
        
        # Message contains substantial code
        if len(message) > 200:  # Long message
            code_indicators = ['import ', 'from ', 'def ', 'class ', 'function ', '<html', '<!DOCTYPE', 'const ', 'let ', 'var ']
            if any(indicator in message for indicator in code_indicators):
                return True
        
        return False
    
    def extract_code_from_message(self, message: str, uploaded_file: Any = None) -> Dict[str, Any]:
        """Extract code and intent from message"""
        
        # Priority: uploaded file
        if uploaded_file and uploaded_file.get('content'):
            return {
                "code": uploaded_file['content'],
                "filename": uploaded_file.get('name', 'app'),
                "intent": message
            }
        
        # Extract code blocks from message
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', message, re.DOTALL)
        
        if code_blocks:
            # Use first significant code block
            code = code_blocks[0].strip()
            # Remove code from intent
            intent = re.sub(r'```(?:\w+)?\n.*?```', '', message, flags=re.DOTALL).strip()
            
            return {
                "code": code,
                "filename": "app",
                "intent": intent or "Build this application"
            }
        
        # No code blocks, treat entire message as code/intent
        return {
            "code": message,
            "filename": "app",
            "intent": "Build this application"
        }
    
    def detect_language(self, code: str) -> str:
        """Detect programming language from code"""
        
        # Python
        if any(keyword in code for keyword in ['import ', 'from ', 'def ', 'class ', 'if __name__']):
            if 'flask' in code.lower() or 'Flask' in code:
                return 'flask'
            elif 'fastapi' in code.lower() or 'FastAPI' in code:
                return 'fastapi'
            return 'python'
        
        # JavaScript/Node
        if any(keyword in code for keyword in ['const ', 'let ', 'var ', 'function ', '=>', 'require(', 'import {']):
            if 'express' in code.lower() or 'Express' in code:
                return 'express'
            elif 'react' in code.lower() or 'React' in code:
                return 'react'
            return 'javascript'
        
        # HTML/Web
        if '<html' in code or '<!DOCTYPE' in code:
            return 'html'
        
        # Default
        return 'python'
    
    async def enhance_code_with_ai(self, code: str, intent: str, language: str) -> str:
        """Use AI to enhance partial code into complete app"""
        
        if not self.model:
            return code
        
        prompt = f"""You are an expert full-stack developer. A user provided this code and wants to build an app.

USER INTENT: {intent}

CODE PROVIDED:
```{language}
{code}
```

YOUR TASK:
1. If the code is complete, return it as-is
2. If it's partial/incomplete, enhance it into a COMPLETE, PRODUCTION-READY application
3. Add all necessary imports, error handling, and best practices
4. For web apps, include both backend AND frontend code

REQUIREMENTS:
- Make it PRODUCTION-READY (no TODO comments, no placeholders)
- Include proper error handling
- Add helpful comments
- Use environment variables for configuration
- Make it immediately runnable

Return ONLY the complete code, no explanations. If it's a web app with frontend+backend, separate them with:
=== BACKEND: filename.py ===
(backend code here)

=== FRONTEND: index.html ===
(frontend code here)
"""
        
        try:
            response = self.model.generate_content(prompt)
            enhanced_code = response.text.strip()
            
            # Remove markdown code blocks if present
            enhanced_code = re.sub(r'```(?:\w+)?\n', '', enhanced_code)
            enhanced_code = enhanced_code.replace('```', '')
            
            return enhanced_code.strip()
        except Exception as e:
            print(f"AI enhancement error: {e}")
            return code
    
    async def build_app_from_chat(self, message: str, uploaded_file: Any = None) -> Dict[str, Any]:
        """Main method: Build complete app from chat message"""
        
        # Extract code and intent
        extracted = self.extract_code_from_message(message, uploaded_file)
        code = extracted['code']
        intent = extracted['intent']
        
        # Detect language
        language = self.detect_language(code)
        
        # Enhance code with AI to make it complete
        enhanced_code = await self.enhance_code_with_ai(code, intent, language)
        
        # Build the app using AppBuilder
        build_result = await self.app_builder.build_app(
            instruction=intent,
            generated_code=enhanced_code,
            language=language
        )
        
        return {
            "success": build_result.get("success", False),
            "app_name": build_result.get("app_name"),
            "app_directory": build_result.get("app_directory"),
            "files_created": build_result.get("files_created", []),
            "language": language,
            "server_status": build_result.get("server_status"),
            "url": build_result.get("url"),
            "message": f"✅ Built complete {language} app: {build_result.get('app_name')}",
            "next_steps": [
                f"📁 App location: {build_result.get('app_directory')}",
                f"📄 Files created: {len(build_result.get('files_created', []))}",
                f"🌐 Access at: {build_result.get('url', 'Check server logs')}",
                "✅ App is running and ready to use!"
            ]
        }


# Global instance
auto_app_builder = AutoAppBuilder()
