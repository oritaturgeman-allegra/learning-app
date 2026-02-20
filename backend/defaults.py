"""
Static defaults and constants for Ariel's English Adventure.
"""

from typing import Dict, List

# App version (single source of truth)
APP_VERSION = "1.6.2"

# Recent changelog entries (shown in "What's New" popup)
APP_CHANGELOG: List[Dict[str, str]] = [
    {
        "version": "1.6.2",
        "text": "Your vocabulary progress now saves — practiced words stay crossed out even after refresh!",
    },
    {
        "version": "1.6.1",
        "text": "Word chips — colorful pill-shaped word tracker with practiced/unpracticed states!",
    },
    {
        "version": "1.6.0",
        "text": "Word tracker sidebar — see all 55 vocabulary words and track your progress!",
    },
]

# App metadata
APP_METADATA = {
    "title": "Ariel's English Adventure",
    "description": "Gamified English learning for kids",
    "version": APP_VERSION,
}
