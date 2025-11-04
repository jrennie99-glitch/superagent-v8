"""
Telegram Bot Builder
Create Telegram bots with natural language commands
Handles commands, inline keyboards, and webhooks
"""

import logging
from typing import Dict, List, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class TelegramBotBuilder:
    """
    Build Telegram bots
    Features:
    - Commands
    - Inline keyboards
    - Webhooks
    - Message handling
    - Callback queries
    """
    
    def __init__(self):
        self.bots = []
    
    def create_telegram_bot(self,
                           bot_name: str,
                           description: str,
                           commands: List[Dict],
                           features: List[str] = None) -> Dict:
        """
        Create a Telegram bot
        
        Args:
            bot_name: Name of the bot
            description: Bot description
            commands: List of commands
            features: Additional features (inline, webhooks, etc.)
        
        Returns:
            Bot configuration and code
        """
        try:
            logger.info(f"Creating Telegram bot: {bot_name}")
            
            features = features or []
            
            # Generate bot code
            bot_code = self._generate_telegram_bot_code(
                bot_name, description, commands, features
            )
            
            bot_info = {
                "success": True,
                "bot_name": bot_name,
                "description": description,
                "code": bot_code,
                "setup_instructions": self._get_setup_instructions(bot_name),
                "commands": commands,
                "features": features
            }
            
            self.bots.append(bot_info)
            return bot_info
            
        except Exception as e:
            logger.error(f"Telegram bot creation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_telegram_bot_code(self,
                                    bot_name: str,
                                    description: str,
                                    commands: List[Dict],
                                    features: List[str]) -> str:
        """Generate Python code for Telegram bot"""
        
        code = f'''"""
{bot_name} - {description}
Telegram Bot built with SuperAgent
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get bot token from environment
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

async def start_command(update: Update, context):
    """Handle /start command"""
    await update.message.reply_text(
        f"Welcome to {bot_name}!\\n\\n"
        f"{description}\\n\\n"
        "Use /help to see available commands."
    )

async def help_command(update: Update, context):
    """Handle /help command"""
    help_text = "Available commands:\\n\\n"
'''
        
        # Add commands
        for cmd in commands:
            cmd_name = cmd.get('name')
            cmd_desc = cmd.get('description', '')
            code += f'    help_text += "/{cmd_name} - {cmd_desc}\\\\n"\n'
        
        code += '''    
    await update.message.reply_text(help_text)

'''
        
        # Add command handlers
        for cmd in commands:
            cmd_name = cmd.get('name')
            cmd_desc = cmd.get('description', '')
            code += f'''
async def {cmd_name}_command(update: Update, context):
    """Handle /{cmd_name} command - {cmd_desc}"""
    user = update.effective_user
    await update.message.reply_text(
        f"Hello {{user.mention_html()}}! Processing /{cmd_name}...",
        parse_mode="HTML"
    )
    # Add your logic here

'''
        
        # Add inline keyboard example if requested
        if 'inline' in features:
            code += '''
async def show_menu(update: Update, context):
    """Show interactive menu"""
    keyboard = [
        [InlineKeyboardButton("Option 1", callback_data="opt1")],
        [InlineKeyboardButton("Option 2", callback_data="opt2")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose an option:", reply_markup=reply_markup)

async def button_handler(update: Update, context):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"You selected: {query.data}")

'''
        
        # Add message handler
        code += '''
async def handle_message(update: Update, context):
    """Handle text messages"""
    text = update.message.text
    await update.message.reply_text(f"You said: {text}")

def main():
    """Start the bot"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
'''
        
        # Add command handlers to main
        for cmd in commands:
            cmd_name = cmd.get('name')
            code += f'    application.add_handler(CommandHandler("{cmd_name}", {cmd_name}_command))\n'
        
        if 'inline' in features:
            code += '    application.add_handler(CallbackQueryHandler(button_handler))\n'
        
        code += '''    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start bot
    logger.info("Bot started!")
    application.run_polling()

if __name__ == "__main__":
    main()
'''
        
        return code
    
    def _get_setup_instructions(self, bot_name: str) -> List[str]:
        """Get setup instructions"""
        return [
            "1. Open Telegram and search for @BotFather",
            "2. Send /newbot command",
            f"3. Enter bot name: {bot_name}",
            "4. Enter bot username (must end in 'bot')",
            "5. Copy the bot token from BotFather",
            "6. Set environment variable: TELEGRAM_BOT_TOKEN=<your-token>",
            "7. Install dependencies: pip install python-telegram-bot",
            "8. Run the bot: python telegram_bot.py",
            "9. Open Telegram and search for your bot",
            "10. Send /start to test the bot"
        ]
    
    def get_bot(self, bot_name: str) -> Optional[Dict]:
        """Get bot by name"""
        for bot in self.bots:
            if bot.get('bot_name') == bot_name:
                return bot
        return None


# Global instance
telegram_bot_builder = TelegramBotBuilder()


def build_telegram_bot(bot_name: str,
                      description: str,
                      commands: List[Dict],
                      features: List[str] = None) -> Dict:
    """
    Build a Telegram bot
    
    Example:
        build_telegram_bot(
            "TaskBot",
            "Manages tasks in Telegram",
            [{"name": "task", "description": "Create a task"}],
            features=["inline"]
        )
    """
    return telegram_bot_builder.create_telegram_bot(bot_name, description, commands, features)
