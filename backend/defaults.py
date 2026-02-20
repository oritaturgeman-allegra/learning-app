"""
Static defaults and constants for Ariel's English Adventure.
"""

from typing import Dict, List

# App version (single source of truth)
APP_VERSION = "1.6.0"

# Recent changelog entries (shown in "What's New" popup)
APP_CHANGELOG: List[Dict[str, str]] = [
    {
        "version": "1.6.0",
        "text": "Word tracker sidebar — see all 55 vocabulary words and track which ones you've practiced!",
    },
    {
        "version": "1.5.1",
        "text": "Completed games get a green checkmark — see your progress at a glance!",
    },
    {
        "version": "1.5.0",
        "text": "Subject tabs on the menu — ready to add Math and more subjects!",
    },
]

# App metadata
APP_METADATA = {
    "title": "Ariel's English Adventure",
    "description": "Gamified English learning for kids",
    "version": APP_VERSION,
}
