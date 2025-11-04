"""Voice interface for SuperAgent - Talk to your AI coding assistant!"""

import asyncio
import os
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import structlog

logger = structlog.get_logger()


class VoiceInterface:
    """
    Voice interface for SuperAgent.
    
    Features:
    - Speech-to-text (STT) for voice commands
    - Text-to-speech (TTS) for voice responses
    - Conversational mode
    - Wake word detection
    - Multi-language support
    - Offline mode support
    """
    
    def __init__(self, agent, config: Optional[Dict[str, Any]] = None):
        """Initialize voice interface.
        
        Args:
            agent: SuperAgent instance
            config: Voice configuration
        """
        self.agent = agent
        self.config = config or {}
        
        # Voice settings
        self.language = self.config.get("language", "en-US")
        self.voice = self.config.get("voice", "default")
        self.wake_word = self.config.get("wake_word", "hey super agent")
        self.enabled = True
        self.listening = False
        
        # Initialize speech recognition
        self.recognizer = None
        self.mic = None
        
        # Initialize TTS engine
        self.tts_engine = None
        
        # Conversation state
        self.conversation_active = False
        self.last_command = None
        
    async def initialize(self):
        """Initialize voice components."""
        try:
            # Initialize speech recognition
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.mic = sr.Microphone()
            
            # Adjust for ambient noise
            logger.info("Calibrating microphone for ambient noise...")
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            logger.info("✓ Speech recognition initialized")
        except ImportError:
            logger.warning("speech_recognition not installed. Install with: pip install SpeechRecognition pyaudio")
            self.recognizer = None
        except Exception as e:
            logger.error(f"Failed to initialize microphone: {e}")
            self.recognizer = None
        
        # Initialize TTS
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            
            # Configure voice
            voices = self.tts_engine.getProperty('voices')
            
            # Try to find a good voice
            if self.voice != "default":
                for voice in voices:
                    if self.voice.lower() in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            # Set properties
            self.tts_engine.setProperty('rate', 175)  # Speed
            self.tts_engine.setProperty('volume', 0.9)  # Volume
            
            logger.info("✓ Text-to-speech initialized")
        except ImportError:
            logger.warning("pyttsx3 not installed. Install with: pip install pyttsx3")
            self.tts_engine = None
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            self.tts_engine = None
    
    async def listen(self, timeout: Optional[int] = None) -> Optional[str]:
        """Listen for voice input.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Recognized text or None
        """
        if not self.recognizer:
            logger.error("Speech recognition not available")
            return None
        
        try:
            logger.info("🎤 Listening...")
            self.listening = True
            
            with self.mic as source:
                # Listen for audio
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=30
                )
            
            self.listening = False
            
            # Recognize speech using Google Speech Recognition
            logger.info("🔄 Processing speech...")
            text = self.recognizer.recognize_google(audio, language=self.language)
            
            logger.info(f"📝 Heard: {text}")
            return text
            
        except Exception as e:
            self.listening = False
            logger.error(f"Speech recognition error: {e}")
            return None
    
    async def speak(self, text: str):
        """Speak text using TTS.
        
        Args:
            text: Text to speak
        """
        if not self.tts_engine:
            # Fallback to printing
            print(f"🤖 SuperAgent: {text}")
            return
        
        try:
            logger.info(f"🔊 Speaking: {text}")
            
            # Run TTS in thread to avoid blocking
            def speak_sync():
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            
            # Run in executor
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, speak_sync)
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            print(f"🤖 SuperAgent: {text}")
    
    async def listen_for_wake_word(self, callback: Optional[Callable] = None) -> bool:
        """Listen for wake word.
        
        Args:
            callback: Optional callback when wake word detected
            
        Returns:
            True if wake word detected
        """
        logger.info(f"👂 Listening for wake word: '{self.wake_word}'")
        
        text = await self.listen(timeout=5)
        
        if text and self.wake_word.lower() in text.lower():
            logger.info("✓ Wake word detected!")
            if callback:
                await callback()
            return True
        
        return False
    
    async def process_voice_command(self, command: str) -> Dict[str, Any]:
        """Process a voice command.
        
        Args:
            command: Voice command text
            
        Returns:
            Command result
        """
        logger.info(f"Processing command: {command}")
        
        # Store last command
        self.last_command = command
        
        # Analyze command intent
        intent = await self._analyze_intent(command)
        
        # Execute based on intent
        if intent["type"] == "create_project":
            return await self._handle_create_project(intent)
        elif intent["type"] == "debug":
            return await self._handle_debug(intent)
        elif intent["type"] == "review":
            return await self._handle_review(intent)
        elif intent["type"] == "query":
            return await self._handle_query(intent)
        elif intent["type"] == "explain":
            return await self._handle_explain(intent)
        elif intent["type"] == "help":
            return await self._handle_help(intent)
        else:
            # Default: treat as code generation instruction
            return await self._handle_create_project({"instruction": command})
    
    async def _analyze_intent(self, command: str) -> Dict[str, Any]:
        """Analyze command intent using AI.
        
        Args:
            command: Voice command
            
        Returns:
            Intent analysis
        """
        command_lower = command.lower()
        
        # Simple keyword-based intent detection
        if any(word in command_lower for word in ["create", "build", "make", "generate"]):
            return {"type": "create_project", "instruction": command}
        elif any(word in command_lower for word in ["debug", "fix", "error"]):
            return {"type": "debug", "target": command}
        elif any(word in command_lower for word in ["review", "check", "analyze"]):
            return {"type": "review", "target": command}
        elif any(word in command_lower for word in ["where", "find", "show me"]):
            return {"type": "query", "question": command}
        elif any(word in command_lower for word in ["explain", "what does", "how does"]):
            return {"type": "explain", "question": command}
        elif any(word in command_lower for word in ["help", "what can you do"]):
            return {"type": "help"}
        else:
            return {"type": "create_project", "instruction": command}
    
    async def _handle_create_project(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle project creation command.
        
        Args:
            intent: Intent data
            
        Returns:
            Result
        """
        instruction = intent.get("instruction", "")
        
        await self.speak(f"Creating project: {instruction}")
        
        result = await self.agent.execute_instruction(instruction)
        
        response = f"Project created successfully! I've generated {len(result.get('results', []))} files."
        await self.speak(response)
        
        return {"success": True, "response": response, "result": result}
    
    async def _handle_debug(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle debug command.
        
        Args:
            intent: Intent data
            
        Returns:
            Result
        """
        await self.speak("Analyzing code for errors...")
        
        # Use current project or last project
        project_path = self.agent.workspace / (self.agent.current_project or "")
        
        if not project_path.exists():
            response = "No project found. Please create a project first."
            await self.speak(response)
            return {"success": False, "response": response}
        
        result = await self.agent.debugger.debug_project(project_path)
        
        error_count = len(result.get("errors", []))
        
        if error_count == 0:
            response = "Great news! No errors found in your code."
        else:
            response = f"Found {error_count} errors. I can fix them for you if you'd like."
        
        await self.speak(response)
        
        return {"success": True, "response": response, "result": result}
    
    async def _handle_review(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code review command.
        
        Args:
            intent: Intent data
            
        Returns:
            Result
        """
        from superagent.modules.code_reviewer import CodeReviewer
        
        await self.speak("Reviewing your code...")
        
        # Find Python files in current project
        project_path = self.agent.workspace / (self.agent.current_project or "")
        py_files = list(project_path.rglob("*.py"))
        
        if not py_files:
            response = "No Python files found to review."
            await self.speak(response)
            return {"success": False, "response": response}
        
        reviewer = CodeReviewer(self.agent.llm)
        review = await reviewer.review_file(py_files[0])
        
        grade = review.get("overall_grade", "N/A")
        security_score = review["scores"]["security"]
        
        response = f"Code review complete. Overall grade: {grade}. Security score: {security_score} out of 100."
        
        await self.speak(response)
        
        return {"success": True, "response": response, "result": review}
    
    async def _handle_query(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle codebase query.
        
        Args:
            intent: Intent data
            
        Returns:
            Result
        """
        from superagent.modules.codebase_query import CodebaseQueryEngine
        
        question = intent.get("question", "")
        
        await self.speak("Let me search the codebase for you...")
        
        project_path = self.agent.workspace / (self.agent.current_project or "")
        
        query_engine = CodebaseQueryEngine(self.agent.llm, self.agent.cache)
        await query_engine.index_codebase(project_path)
        
        result = await query_engine.query(question, project_path)
        answer = result.get("answer", "I couldn't find an answer.")
        
        await self.speak(answer)
        
        return {"success": True, "response": answer, "result": result}
    
    async def _handle_explain(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code explanation request.
        
        Args:
            intent: Intent data
            
        Returns:
            Result
        """
        question = intent.get("question", "")
        
        await self.speak("Let me explain that for you...")
        
        # Use LLM to explain
        explanation = await self.agent.llm.generate(
            f"Explain in simple terms: {question}"
        )
        
        # Shorten for voice
        short_explanation = explanation[:200] + "..." if len(explanation) > 200 else explanation
        
        await self.speak(short_explanation)
        
        return {"success": True, "response": short_explanation, "full": explanation}
    
    async def _handle_help(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle help request.
        
        Args:
            intent: Intent data
            
        Returns:
            Result
        """
        help_text = """I can help you with:
- Creating projects: Say 'Create a REST API with authentication'
- Debugging code: Say 'Debug my code'
- Code review: Say 'Review my code'
- Answering questions: Say 'Where is authentication implemented?'
- Explaining code: Say 'Explain how this works'

What would you like me to do?"""
        
        await self.speak(help_text)
        
        return {"success": True, "response": help_text}
    
    async def conversation_mode(self):
        """Enter conversation mode for continuous interaction."""
        logger.info("🎙️ Entering conversation mode")
        
        await self.speak("Hello! I'm SuperAgent. How can I help you today?")
        
        self.conversation_active = True
        
        while self.conversation_active:
            try:
                # Listen for command
                command = await self.listen(timeout=30)
                
                if not command:
                    continue
                
                # Check for exit commands
                if any(word in command.lower() for word in ["goodbye", "exit", "stop", "quit"]):
                    await self.speak("Goodbye! Let me know if you need anything else.")
                    self.conversation_active = False
                    break
                
                # Process command
                result = await self.process_voice_command(command)
                
            except KeyboardInterrupt:
                await self.speak("Conversation ended.")
                self.conversation_active = False
                break
            except Exception as e:
                logger.error(f"Conversation error: {e}")
                await self.speak("Sorry, I encountered an error. Please try again.")
    
    async def wake_word_mode(self):
        """Listen for wake word continuously."""
        logger.info(f"👂 Wake word mode active. Say '{self.wake_word}' to activate.")
        
        await self.speak(f"Wake word mode active. Say {self.wake_word} when you need me.")
        
        while True:
            try:
                if await self.listen_for_wake_word():
                    await self.speak("Yes? How can I help?")
                    
                    # Listen for command
                    command = await self.listen(timeout=10)
                    
                    if command:
                        await self.process_voice_command(command)
                    else:
                        await self.speak("I didn't catch that. Say the wake word again when you're ready.")
                
            except KeyboardInterrupt:
                await self.speak("Wake word mode deactivated.")
                break
            except Exception as e:
                logger.error(f"Wake word mode error: {e}")
    
    def stop_listening(self):
        """Stop listening."""
        self.listening = False
        self.conversation_active = False





