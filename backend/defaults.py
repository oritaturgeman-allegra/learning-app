"""
Static defaults and constants for Ariel's English Adventure.
"""

from typing import Dict, List

# App version (single source of truth)
APP_VERSION = "1.5.0"

# Recent changelog entries (shown in "What's New" popup)
APP_CHANGELOG: List[Dict[str, str]] = [
    {
        "version": "1.5.0",
        "text": "Subject tabs on the menu — ready to add Math and more subjects!",
    },
    {
        "version": "1.4.2",
        "text": "Session celebration — fireworks and trophy popup after completing all 4 games!",
    },
    {
        "version": "1.4.1",
        "text": "Shuffle button on menu — ensures different questions each practice session",
    },
]

# App metadata
APP_METADATA = {
    "title": "Ariel's English Adventure",
    "description": "Gamified English learning for kids",
    "version": APP_VERSION,
}
