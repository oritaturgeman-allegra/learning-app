"""
Static defaults and constants for Ariel's English Adventure.
"""

from typing import Dict, List

# App version (single source of truth)
APP_VERSION = "1.2.0"

# Recent changelog entries (shown in "What's New" popup)
APP_CHANGELOG: List[Dict[str, str]] = [
    {
        "version": "1.2.0",
        "text": "Cleaned up codebase — removed old newsletter code, streamlined for learning app",
    },
    {
        "version": "1.1.0",
        "text": "Your progress is saved! Stars and game results now persist in the database",
    },
    {
        "version": "1.0.0",
        "text": "Ariel's English Adventure — 4 fun learning games with stars, sounds, and animations",
    },
]

# App metadata
APP_METADATA = {
    "title": "Ariel's English Adventure",
    "description": "Gamified English learning for kids",
    "version": APP_VERSION,
}
