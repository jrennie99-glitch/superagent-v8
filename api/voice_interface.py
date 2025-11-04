"""
Enhanced Voice Interface Module
Provides advanced voice control with wake word detection and text-to-speech
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

class VoiceInterface:
    """Enhanced voice interface with wake word detection and TTS"""
    
    def __init__(self):
        self.wake_words = ["hey agent", "super agent", "agent"]
        self.commands = {
            "generate": ["generate", "create", "build", "make"],
            "explain": ["explain", "describe", "what is", "tell me about"],
            "fix": ["fix", "debug", "repair", "correct"],
            "test": ["test", "check", "verify", "validate"],
            "deploy": ["deploy", "publish", "launch", "release"],
            "help": ["help", "assist", "guide", "support"]
        }
        self.session_history = []
        
    def detect_wake_word(self, text: str) -> bool:
        """Detect if wake word is present in text"""
        text_lower = text.lower()
        return any(wake_word in text_lower for wake_word in self.wake_words)
    
    def parse_voice_command(self, text: str) -> Dict[str, Any]:
        """Parse voice command into structured format"""
        text_lower = text.lower()
        
        # Remove wake word if present
        for wake_word in self.wake_words:
            text_lower = text_lower.replace(wake_word, "").strip()
        
        # Detect command type
        command_type = "unknown"
        for cmd_name, keywords in self.commands.items():
            if any(keyword in text_lower for keyword in keywords):
                command_type = cmd_name
                break
        
        # Extract language if mentioned
        languages = ["python", "javascript", "typescript", "go", "rust", "java", "c++", "c"]
        detected_language = None
        for lang in languages:
            if lang in text_lower:
                detected_language = lang
                break
        
        return {
            "raw_text": text,
            "command_type": command_type,
            "language": detected_language,
            "timestamp": datetime.utcnow().isoformat(),
            "wake_word_detected": self.detect_wake_word(text)
        }
    
    def generate_tts_response(self, response_text: str, emotion: str = "neutral") -> Dict[str, Any]:
        """Generate text-to-speech response with emotion"""
        return {
            "text": response_text,
            "emotion": emotion,
            "voice": "default",
            "speed": 1.0,
            "pitch": 1.0,
            "volume": 0.8,
            "ssml": self._generate_ssml(response_text, emotion)
        }
    
    def _generate_ssml(self, text: str, emotion: str) -> str:
        """Generate SSML markup for enhanced TTS"""
        rate = "medium"
        pitch = "medium"
        
        if emotion == "excited":
            rate = "fast"
            pitch = "high"
        elif emotion == "calm":
            rate = "slow"
            pitch = "low"
        
        ssml = f"""
        <speak>
            <prosody rate="{rate}" pitch="{pitch}">
                {text}
            </prosody>
        </speak>
        """
        return ssml.strip()
    
    def process_voice_input(self, audio_text: str) -> Dict[str, Any]:
        """Process voice input and return structured response"""
        # Parse command
        parsed = self.parse_voice_command(audio_text)
        
        # Generate response based on command type
        response_text = self._generate_response_text(parsed)
        
        # Create TTS response
        emotion = "excited" if parsed["command_type"] != "unknown" else "neutral"
        tts_response = self.generate_tts_response(response_text, emotion)
        
        # Log to session history
        self.session_history.append({
            "input": parsed,
            "output": tts_response,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "parsed_command": parsed,
            "response": tts_response,
            "success": True
        }
    
    def _generate_response_text(self, parsed: Dict[str, Any]) -> str:
        """Generate appropriate response text based on parsed command"""
        responses = {
            "generate": "I'll generate that code for you right away.",
            "explain": "Let me explain that for you.",
            "fix": "I'll analyze and fix the issue.",
            "test": "Running tests now.",
            "deploy": "Preparing deployment configuration.",
            "help": "I'm here to help! What would you like to do?",
            "unknown": "I'm not sure what you want me to do. Could you rephrase that?"
        }
        
        return responses.get(parsed["command_type"], responses["unknown"])
    
    def get_voice_stats(self) -> Dict[str, Any]:
        """Get voice interface statistics"""
        total_commands = len(self.session_history)
        command_types = {}
        
        for entry in self.session_history:
            cmd_type = entry["input"]["command_type"]
            command_types[cmd_type] = command_types.get(cmd_type, 0) + 1
        
        return {
            "total_commands": total_commands,
            "command_breakdown": command_types,
            "supported_wake_words": self.wake_words,
            "supported_commands": list(self.commands.keys()),
            "session_start": self.session_history[0]["timestamp"] if self.session_history else None
        }
    
    def get_available_voices(self) -> List[Dict[str, str]]:
        """Get list of available TTS voices"""
        return [
            {"id": "default", "name": "Default Voice", "language": "en-US", "gender": "neutral"},
            {"id": "male", "name": "Male Voice", "language": "en-US", "gender": "male"},
            {"id": "female", "name": "Female Voice", "language": "en-US", "gender": "female"},
            {"id": "robotic", "name": "Robotic Voice", "language": "en-US", "gender": "neutral"}
        ]
    
    def configure_voice(self, voice_id: str, speed: float = 1.0, pitch: float = 1.0) -> Dict[str, Any]:
        """Configure voice settings"""
        return {
            "voice_id": voice_id,
            "speed": max(0.5, min(2.0, speed)),
            "pitch": max(0.5, min(2.0, pitch)),
            "configured": True
        }

# Advanced Speech-to-Text and Text-to-Speech Integration
class AdvancedVoiceInterface(VoiceInterface):
    """Advanced voice interface with STT and TTS support"""
    
    def __init__(self):
        super().__init__()
        self.stt_provider = "google"  # google, azure, deepgram
        self.tts_provider = "google"  # google, azure, elevenlabs
        self.audio_cache = {}
        self.enable_wake_word = True
        self.enable_caching = True
    
    async def speech_to_text(self, audio_data: bytes, language: str = "en-US") -> Dict[str, Any]:
        """Convert speech to text using configured provider"""
        try:
            if self.stt_provider == "google":
                return await self._google_stt(audio_data, language)
            elif self.stt_provider == "azure":
                return await self._azure_stt(audio_data, language)
            elif self.stt_provider == "deepgram":
                return await self._deepgram_stt(audio_data, language)
            else:
                return {"error": "STT provider not configured"}
        except Exception as e:
            return {"error": f"STT error: {str(e)}"}
    
    async def _google_stt(self, audio_data: bytes, language: str) -> Dict[str, Any]:
        """Google Cloud Speech-to-Text"""
        try:
            # Check cache first
            cache_key = f"stt_google_{hash(audio_data)}_{language}"
            if self.enable_caching and cache_key in self.audio_cache:
                return self.audio_cache[cache_key]
            
            # Placeholder for actual Google STT implementation
            result = {
                "text": "[Transcribed text from Google STT]",
                "confidence": 0.95,
                "provider": "google",
                "language": language,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if self.enable_caching:
                self.audio_cache[cache_key] = result
            
            return result
        except Exception as e:
            return {"error": f"Google STT error: {str(e)}"}
    
    async def _azure_stt(self, audio_data: bytes, language: str) -> Dict[str, Any]:
        """Azure Speech-to-Text"""
        try:
            result = {
                "text": "[Transcribed text from Azure STT]",
                "confidence": 0.93,
                "provider": "azure",
                "language": language,
                "timestamp": datetime.utcnow().isoformat()
            }
            return result
        except Exception as e:
            return {"error": f"Azure STT error: {str(e)}"}
    
    async def _deepgram_stt(self, audio_data: bytes, language: str) -> Dict[str, Any]:
        """Deepgram Speech-to-Text"""
        try:
            result = {
                "text": "[Transcribed text from Deepgram STT]",
                "confidence": 0.94,
                "provider": "deepgram",
                "language": language,
                "timestamp": datetime.utcnow().isoformat()
            }
            return result
        except Exception as e:
            return {"error": f"Deepgram STT error: {str(e)}"}
    
    async def text_to_speech(self, text: str, voice: str = "default") -> Dict[str, Any]:
        """Convert text to speech using configured provider"""
        try:
            if self.tts_provider == "google":
                return await self._google_tts(text, voice)
            elif self.tts_provider == "azure":
                return await self._azure_tts(text, voice)
            elif self.tts_provider == "elevenlabs":
                return await self._elevenlabs_tts(text, voice)
            else:
                return {"error": "TTS provider not configured"}
        except Exception as e:
            return {"error": f"TTS error: {str(e)}"}
    
    async def _google_tts(self, text: str, voice: str) -> Dict[str, Any]:
        """Google Cloud Text-to-Speech"""
        try:
            cache_key = f"tts_google_{hash(text)}_{voice}"
            if self.enable_caching and cache_key in self.audio_cache:
                return self.audio_cache[cache_key]
            
            result = {
                "audio": b"[MP3 audio data from Google TTS]",
                "provider": "google",
                "voice": voice,
                "format": "mp3",
                "duration_ms": len(text) * 50,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if self.enable_caching:
                self.audio_cache[cache_key] = result
            
            return result
        except Exception as e:
            return {"error": f"Google TTS error: {str(e)}"}
    
    async def _azure_tts(self, text: str, voice: str) -> Dict[str, Any]:
        """Azure Text-to-Speech"""
        try:
            result = {
                "audio": b"[WAV audio data from Azure TTS]",
                "provider": "azure",
                "voice": voice,
                "format": "wav",
                "duration_ms": len(text) * 50,
                "timestamp": datetime.utcnow().isoformat()
            }
            return result
        except Exception as e:
            return {"error": f"Azure TTS error: {str(e)}"}
    
    async def _elevenlabs_tts(self, text: str, voice: str) -> Dict[str, Any]:
        """ElevenLabs Text-to-Speech"""
        try:
            result = {
                "audio": b"[MP3 audio data from ElevenLabs TTS]",
                "provider": "elevenlabs",
                "voice": voice,
                "format": "mp3",
                "duration_ms": len(text) * 50,
                "timestamp": datetime.utcnow().isoformat()
            }
            return result
        except Exception as e:
            return {"error": f"ElevenLabs TTS error: {str(e)}"}
    
    def set_stt_provider(self, provider: str) -> Dict[str, Any]:
        """Set speech-to-text provider"""
        if provider in ["google", "azure", "deepgram", "openai"]:
            self.stt_provider = provider
            return {"status": "success", "provider": provider}
        return {"error": f"Unknown STT provider: {provider}"}
    
    def set_tts_provider(self, provider: str) -> Dict[str, Any]:
        """Set text-to-speech provider"""
        if provider in ["google", "azure", "elevenlabs", "openai"]:
            self.tts_provider = provider
            return {"status": "success", "provider": provider}
        return {"error": f"Unknown TTS provider: {provider}"}
    
    def get_voice_stats(self) -> Dict[str, Any]:
        """Get enhanced voice statistics"""
        stats = super().get_voice_stats()
        stats.update({
            "stt_provider": self.stt_provider,
            "tts_provider": self.tts_provider,
            "cache_size": len(self.audio_cache),
            "caching_enabled": self.enable_caching,
            "wake_word_detection": self.enable_wake_word
        })
        return stats

# Global instances
voice_interface = VoiceInterface()
advanced_voice_interface = AdvancedVoiceInterface()
