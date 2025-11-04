"""
First-Party Connectors Framework
OAuth integrations for popular services
"""

from .github_connector import GitHubConnector
from .google_connector import GoogleConnector
from .notion_connector import NotionConnector
from .slack_connector import SlackConnector

__all__ = [
    'GitHubConnector',
    'GoogleConnector',
    'NotionConnector',
    'SlackConnector'
]
