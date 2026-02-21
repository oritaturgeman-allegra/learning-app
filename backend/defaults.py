"""
Static defaults and constants for Ariel's English Adventure.
"""

from typing import Dict, List

# App version (single source of truth)
APP_VERSION = "1.8.0"

# Recent changelog entries (shown in "What's New" popup)
APP_CHANGELOG: List[Dict[str, str]] = [
    {
        "version": "1.8.0",
        "text": "Every word counts! Play all 4 games and practice ALL 55 words — no more gaps!",
    },
    {
        "version": "1.7.0",
        "text": "Fresh start button — reset your word tracker for a new practice round, your stars stay forever!",
    },
    {
        "version": "1.6.3",
        "text": "Word chips got a makeover — purple before practice, sage green after, with a fun bounce animation!",
    },
]

# App metadata
APP_METADATA = {
    "title": "Ariel's English Adventure",
    "description": "Gamified English learning for kids",
    "version": APP_VERSION,
}
