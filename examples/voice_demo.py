"""Voice interface demonstration for SuperAgent."""

import asyncio
from superagent import SuperAgent, Config
from superagent.modules.voice_interface import VoiceInterface


async def demo_voice_commands():
    """
    Demonstrate voice interface capabilities.
    
    This example shows how to:
    1. Initialize voice interface
    2. Process voice commands
    3. Use text-to-speech responses
    """
    
    print("=" * 60)
    print("SuperAgent Voice Interface Demo")
    print("=" * 60)
    
    config = Config()
    
    async with SuperAgent(config) as agent:
        # Initialize voice interface
        voice_config = {
            "language": "en-US",
            "voice": "default",
            "wake_word": "hey super agent"
        }
        
        voice_interface = VoiceInterface(agent, voice_config)
        
        print("\n1. Initializing voice interface...")
        await voice_interface.initialize()
        
        if not voice_interface.recognizer:
            print("\n❌ Voice recognition not available!")
            print("\nTo enable voice features, install:")
            print("  pip install SpeechRecognition pyaudio pyttsx3")
            print("\nContinuing with text-to-speech demo only...\n")
            
            # Demo TTS only
            if voice_interface.tts_engine:
                print("2. Text-to-Speech Demo:")
                await voice_interface.speak("Hello! I am SuperAgent, your AI coding assistant.")
                await voice_interface.speak("I can help you create projects, debug code, and much more.")
            
            return
        
        print("✓ Voice interface ready!\n")
        
        # Demo 1: Simple voice recognition
        print("2. Voice Recognition Test:")
        print("   Say something (you have 5 seconds)...")
        
        text = await voice_interface.listen(timeout=5)
        
        if text:
            print(f"   ✓ You said: {text}")
            await voice_interface.speak(f"I heard you say: {text}")
        else:
            print("   No speech detected.")
        
        # Demo 2: Process simulated voice commands
        print("\n3. Processing Voice Commands:")
        
        test_commands = [
            "Create a simple calculator in Python",
            "Where is the main function?",
            "Explain how this works",
        ]
        
        for cmd in test_commands:
            print(f"\n   Command: '{cmd}'")
            
            # Simulate voice input (in real use, this would be from microphone)
            result = await voice_interface.process_voice_command(cmd)
            
            print(f"   ✓ Response: {result.get('response', '')[:100]}...")
        
        # Demo 3: Interactive mode (optional)
        print("\n4. Interactive Voice Mode:")
        print("   Would you like to try conversation mode? (y/n)")
        
        try:
            choice = input("   > ").strip().lower()
            
            if choice == 'y':
                print("\n   Starting conversation mode...")
                print("   Say 'goodbye' to exit.\n")
                
                # Enter conversation mode
                await voice_interface.conversation_mode()
        except KeyboardInterrupt:
            print("\n   Skipped.")
        
        print("\n" + "=" * 60)
        print("Voice Interface Demo Complete!")
        print("=" * 60)
        
        print("\nVoice Features Demonstrated:")
        print("  ✓ Speech-to-text recognition")
        print("  ✓ Text-to-speech responses")
        print("  ✓ Command processing")
        print("  ✓ Conversation mode")
        
        print("\nTo use voice interface:")
        print("  1. CLI: superagent voice talk")
        print("  2. Wake word: superagent voice listen")
        print("  3. Python: Use VoiceInterface class")
        
        print("\n🎤 Talk to SuperAgent anytime!")


async def demo_wake_word():
    """Demonstrate wake word detection (requires user interaction)."""
    
    print("\n" + "=" * 60)
    print("Wake Word Detection Demo")
    print("=" * 60)
    
    config = Config()
    
    async with SuperAgent(config) as agent:
        voice_interface = VoiceInterface(agent, {"wake_word": "hey super agent"})
        
        await voice_interface.initialize()
        
        if not voice_interface.recognizer:
            print("\nVoice recognition not available.")
            return
        
        print("\nSay 'hey super agent' to activate...")
        print("Press Ctrl+C to cancel.\n")
        
        try:
            detected = await voice_interface.listen_for_wake_word()
            
            if detected:
                print("✓ Wake word detected!")
                await voice_interface.speak("Yes? How can I help?")
            else:
                print("Wake word not detected. Try again.")
        except KeyboardInterrupt:
            print("\nDemo cancelled.")


if __name__ == "__main__":
    print("\nSuperAgent Voice Interface")
    print("==========================\n")
    print("Choose demo:")
    print("  1. Voice commands demo")
    print("  2. Wake word demo")
    print("  3. Both\n")
    
    try:
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            asyncio.run(demo_voice_commands())
        elif choice == "2":
            asyncio.run(demo_wake_word())
        elif choice == "3":
            asyncio.run(demo_voice_commands())
            asyncio.run(demo_wake_word())
        else:
            print("Invalid choice. Running full demo...")
            asyncio.run(demo_voice_commands())
    except KeyboardInterrupt:
        print("\n\nDemo cancelled. Goodbye!")





