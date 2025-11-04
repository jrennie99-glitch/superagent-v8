"""Voice interface CLI commands for SuperAgent."""

import asyncio
import click
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
import structlog

from superagent.core.agent import SuperAgent
from superagent.core.config import Config
from superagent.modules.voice_interface import VoiceInterface

console = Console()
logger = structlog.get_logger()


@click.group()
def voice():
    """Voice interface commands for SuperAgent."""
    pass


@voice.command()
@click.option('--language', '-l', default='en-US', help='Language (e.g., en-US, es-ES)')
@click.option('--voice', '-v', default='default', help='Voice name')
@click.option('--config', '-c', help='Configuration file')
def talk(language, voice, config):
    """
    Talk to SuperAgent using your voice!
    
    Start a conversation with SuperAgent where you can give commands
    by speaking naturally.
    
    Example:
        superagent voice talk
        
    Then say: "Create a REST API with user authentication"
    """
    console.print(Panel.fit(
        "[bold cyan]SuperAgent Voice Interface[/bold cyan]\n\n"
        "🎤 Get ready to talk to SuperAgent!\n\n"
        "You can say things like:\n"
        "  • 'Create a web app with authentication'\n"
        "  • 'Debug my code'\n"
        "  • 'Review my code'\n"
        "  • 'Where is the login function?'\n"
        "  • 'Explain how caching works'\n\n"
        "Say 'goodbye' or 'exit' to end the conversation.",
        title="Voice Mode"
    ))
    
    async def run():
        cfg = Config(config) if config else Config()
        
        async with SuperAgent(cfg) as agent:
            voice_config = {
                "language": language,
                "voice": voice
            }
            
            voice_interface = VoiceInterface(agent, voice_config)
            
            console.print("\n[dim]Initializing voice interface...[/dim]")
            await voice_interface.initialize()
            
            if not voice_interface.recognizer:
                console.print("\n[red]❌ Voice recognition not available![/red]")
                console.print("\nPlease install required packages:")
                console.print("  pip install SpeechRecognition pyaudio pyttsx3")
                return
            
            console.print("\n[green]✓ Voice interface ready![/green]")
            console.print("[bold]Start speaking...[/bold]\n")
            
            # Enter conversation mode
            await voice_interface.conversation_mode()
    
    asyncio.run(run())


@voice.command()
@click.option('--wake-word', '-w', default='hey super agent', help='Wake word phrase')
@click.option('--language', '-l', default='en-US', help='Language')
@click.option('--config', '-c', help='Configuration file')
def listen(wake_word, language, config):
    """
    Start wake word detection mode.
    
    SuperAgent will listen for the wake word, then execute your command.
    
    Example:
        superagent voice listen --wake-word "hey super agent"
        
    Then say: "Hey super agent, create a todo app"
    """
    console.print(Panel.fit(
        f"[bold magenta]Wake Word Mode[/bold magenta]\n\n"
        f"👂 Listening for: '{wake_word}'\n\n"
        f"Say the wake word followed by your command.\n"
        f"Press Ctrl+C to exit.",
        title="Wake Word Detection"
    ))
    
    async def run():
        cfg = Config(config) if config else Config()
        
        async with SuperAgent(cfg) as agent:
            voice_config = {
                "language": language,
                "wake_word": wake_word
            }
            
            voice_interface = VoiceInterface(agent, voice_config)
            
            console.print("\n[dim]Initializing...[/dim]")
            await voice_interface.initialize()
            
            if not voice_interface.recognizer:
                console.print("\n[red]❌ Voice recognition not available![/red]")
                return
            
            console.print("\n[green]✓ Ready![/green]")
            console.print(f"\n[bold]Say '{wake_word}' to activate...[/bold]\n")
            
            await voice_interface.wake_word_mode()
    
    asyncio.run(run())


@voice.command()
@click.argument('text')
@click.option('--voice', '-v', default='default', help='Voice name')
def speak(text, voice):
    """
    Make SuperAgent speak text (TTS demo).
    
    Example:
        superagent voice speak "Hello, I am SuperAgent"
    """
    async def run():
        cfg = Config()
        
        async with SuperAgent(cfg) as agent:
            voice_config = {"voice": voice}
            voice_interface = VoiceInterface(agent, voice_config)
            
            await voice_interface.initialize()
            await voice_interface.speak(text)
    
    asyncio.run(run())


@voice.command()
@click.option('--timeout', '-t', default=5, help='Listening timeout in seconds')
def test(timeout):
    """
    Test voice recognition (microphone check).
    
    Example:
        superagent voice test
    """
    console.print(Panel.fit(
        "[bold yellow]Microphone Test[/bold yellow]\n\n"
        "🎤 Testing voice recognition...\n"
        "Speak clearly into your microphone.",
        title="Voice Test"
    ))
    
    async def run():
        cfg = Config()
        
        async with SuperAgent(cfg) as agent:
            voice_interface = VoiceInterface(agent)
            
            console.print("\n[dim]Initializing...[/dim]")
            await voice_interface.initialize()
            
            if not voice_interface.recognizer:
                console.print("\n[red]❌ Microphone not available![/red]")
                console.print("\nInstall: pip install SpeechRecognition pyaudio")
                return
            
            console.print("\n[green]✓ Microphone ready![/green]")
            console.print(f"\n[bold]Speak now (you have {timeout} seconds)...[/bold]\n")
            
            text = await voice_interface.listen(timeout=timeout)
            
            if text:
                console.print(f"\n[green]✓ Recognized:[/green] {text}")
            else:
                console.print("\n[yellow]No speech detected. Try again.[/yellow]")
    
    asyncio.run(run())


@voice.command()
def install():
    """
    Install voice interface dependencies.
    
    This will guide you through installing the required packages.
    """
    console.print(Panel.fit(
        "[bold blue]Voice Interface Setup[/bold blue]\n\n"
        "Installing voice interface dependencies...",
        title="Installation"
    ))
    
    console.print("\n[bold]Step 1: Install Python packages[/bold]")
    console.print("Run these commands:\n")
    console.print("  [cyan]pip install SpeechRecognition[/cyan]")
    console.print("  [cyan]pip install pyaudio[/cyan]")
    console.print("  [cyan]pip install pyttsx3[/cyan]")
    
    console.print("\n[bold]Step 2: Install system dependencies[/bold]")
    console.print("\n[yellow]macOS:[/yellow]")
    console.print("  brew install portaudio")
    
    console.print("\n[yellow]Linux (Ubuntu/Debian):[/yellow]")
    console.print("  sudo apt-get install portaudio19-dev python3-pyaudio")
    
    console.print("\n[yellow]Windows:[/yellow]")
    console.print("  PyAudio wheels: pipwin install pyaudio")
    
    console.print("\n[bold]Step 3: Test your setup[/bold]")
    console.print("  [cyan]superagent voice test[/cyan]")
    
    console.print("\n[green]✓ Installation guide complete![/green]")
    console.print("\nRun [bold]superagent voice talk[/bold] when ready!\n")


if __name__ == "__main__":
    voice()





