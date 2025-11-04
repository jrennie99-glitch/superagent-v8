"""
Slack Agent Builder
Create Slack bots and agents with natural language commands
Handles webhooks, slash commands, and interactive messages
"""

import logging
from typing import Dict, List, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class SlackAgentBuilder:
    """
    Build Slack agents and bots
    Features:
    - Slash commands
    - Interactive messages
    - Event subscriptions
    - Bot users
    - Webhook integrations
    """
    
    def __init__(self):
        self.agents = []
    
    def create_slack_bot(self, 
                        bot_name: str,
                        description: str,
                        commands: List[Dict],
                        features: List[str] = None) -> Dict:
        """
        Create a Slack bot
        
        Args:
            bot_name: Name of the bot
            description: Bot description
            commands: List of slash commands
            features: Additional features (events, interactive, etc.)
        
        Returns:
            Bot configuration and code
        """
        try:
            logger.info(f"Creating Slack bot: {bot_name}")
            
            features = features or []
            
            # Generate bot code
            bot_code = self._generate_slack_bot_code(
                bot_name, description, commands, features
            )
            
            # Generate configuration
            config = self._generate_slack_config(bot_name, commands, features)
            
            bot_info = {
                "success": True,
                "bot_name": bot_name,
                "description": description,
                "code": bot_code,
                "config": config,
                "setup_instructions": self._get_setup_instructions(bot_name),
                "commands": commands,
                "features": features
            }
            
            self.agents.append(bot_info)
            return bot_info
            
        except Exception as e:
            logger.error(f"Slack bot creation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_slack_bot_code(self, 
                                bot_name: str,
                                description: str,
                                commands: List[Dict],
                                features: List[str]) -> str:
        """Generate Python code for Slack bot"""
        
        code = f'''"""
{bot_name} - {description}
Slack Bot built with SuperAgent
"""

from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
import os

# Initialize Slack app
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

'''
        
        # Add command handlers
        for cmd in commands:
            cmd_name = cmd.get('name')
            cmd_desc = cmd.get('description', '')
            code += f'''
@app.command("/{cmd_name}")
def handle_{cmd_name}(ack, say, command):
    """Handle /{cmd_name} command - {cmd_desc}"""
    ack()
    user = command['user_name']
    say(f"Hello <@{{command['user_id']}}>! Processing your request...")
    # Add your logic here
    
'''
        
        # Add event handlers if requested
        if 'events' in features:
            code += '''
@app.event("message")
def handle_message_events(body, logger):
    """Handle message events"""
    logger.info(body)
    
'''
        
        # Add Flask route
        code += '''
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    """Handle Slack events"""
    return handler.handle(request)

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=3000)
'''
        
        return code
    
    def _generate_slack_config(self, 
                              bot_name: str,
                              commands: List[Dict],
                              features: List[str]) -> Dict:
        """Generate Slack app configuration"""
        
        config = {
            "display_information": {
                "name": bot_name,
                "description": f"AI-powered Slack bot",
                "background_color": "#9333EA"
            },
            "features": {
                "bot_user": {
                    "display_name": bot_name,
                    "always_online": True
                }
            },
            "oauth_config": {
                "scopes": {
                    "bot": [
                        "commands",
                        "chat:write",
                        "channels:read"
                    ]
                }
            },
            "settings": {
                "event_subscriptions": {
                    "request_url": "https://your-app.repl.co/slack/events",
                    "bot_events": ["message.channels"] if 'events' in features else []
                },
                "interactivity": {
                    "is_enabled": 'interactive' in features,
                    "request_url": "https://your-app.repl.co/slack/events"
                },
                "org_deploy_enabled": False,
                "socket_mode_enabled": False,
                "token_rotation_enabled": False
            }
        }
        
        return config
    
    def _get_setup_instructions(self, bot_name: str) -> List[str]:
        """Get setup instructions"""
        return [
            "1. Go to https://api.slack.com/apps",
            "2. Click 'Create New App' → 'From scratch'",
            f"3. Name it '{bot_name}' and select your workspace",
            "4. Go to 'OAuth & Permissions' → Add Bot Token Scopes: commands, chat:write",
            "5. Install the app to your workspace",
            "6. Copy 'Bot User OAuth Token' → Set as SLACK_BOT_TOKEN",
            "7. Go to 'Basic Information' → Copy 'Signing Secret' → Set as SLACK_SIGNING_SECRET",
            "8. Go to 'Slash Commands' → Create commands as needed",
            "9. Set Request URL to: https://your-app.repl.co/slack/events",
            "10. Install dependencies: pip install slack-bolt flask",
            "11. Run the bot: python slack_bot.py"
        ]
    
    def get_agent(self, bot_name: str) -> Optional[Dict]:
        """Get agent by name"""
        for agent in self.agents:
            if agent.get('bot_name') == bot_name:
                return agent
        return None


# Global instance
slack_agent_builder = SlackAgentBuilder()


def build_slack_bot(bot_name: str, 
                   description: str,
                   commands: List[Dict],
                   features: List[str] = None) -> Dict:
    """
    Build a Slack bot
    
    Example:
        build_slack_bot(
            "TaskBot",
            "Manages tasks in Slack",
            [{"name": "task", "description": "Create a task"}],
            features=["events", "interactive"]
        )
    """
    return slack_agent_builder.create_slack_bot(bot_name, description, commands, features)
