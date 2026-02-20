"""
Static defaults and constants for Ariel's English Adventure.
"""

from typing import Dict, List

# App version (single source of truth)
APP_VERSION = "1.4.2"

# Recent changelog entries (shown in "What's New" popup)
APP_CHANGELOG: List[Dict[str, str]] = [
    {
        "version": "1.4.2",
        "text": "Session celebration — fireworks and trophy popup after completing all 4 games!",
    },
    {
        "version": "1.4.1",
        "text": "Shuffle button on menu — ensures different questions each practice session",
    },
    {
        "version": "1.4.0",
        "text": "Added all 55 vocabulary words from Jet 2 Unit 2 + new sentences, restructured for future unit support",
    },
]

# App metadata
APP_METADATA = {
    "title": "Ariel's English Adventure",
    "description": "Gamified English learning for kids",
    "version": APP_VERSION,
}
