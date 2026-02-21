"""
Static defaults and constants for Ariel's English Adventure.
"""

from typing import Any, Dict, List

# App version (single source of truth)
APP_VERSION = "2.0.0"

# Recent changelog entries (shown in "What's New" popup)
APP_CHANGELOG: List[Dict[str, str]] = [
    {
        "version": "2.0.0",
        "text": "Word tracker now remembers ALL your words — even from sentences! No more missing words after refresh",
    },
    {
        "version": "1.9.0",
        "text": "Collect reward cards as you earn stars! 6 cards to unlock — tap the trophy to see your collection",
    },
    {
        "version": "1.8.0",
        "text": "Every word counts! Play all 4 games and practice ALL 55 words — no more gaps!",
    },
]

# Collectible reward tiers — unlocked at star milestones
REWARD_TIERS: List[Dict[str, Any]] = [
    {"stars": 25, "id": "spark", "name_en": "Spark", "name_he": "ניצוץ", "emoji": "✨", "description_he": "ההרפתקה רק מתחילה!"},
    {"stars": 50, "id": "slay", "name_en": "Slay", "name_he": "סלייי", "emoji": "💅", "description_he": "את פשוט שולטת בזה!"},
    {"stars": 100, "id": "fire", "name_en": "Fire", "name_he": "פייר", "emoji": "🔥", "description_he": "בלתי ניתנת לעצירה!"},
    {"stars": 150, "id": "unicorn", "name_en": "Unicorn", "name_he": "חד-קרן", "emoji": "🦄", "description_he": "נדירה וקסומה!"},
    {"stars": 200, "id": "goat", "name_en": "GOAT", "name_he": "גואט", "emoji": "🐐", "description_he": "הכי טובה שיש!"},
    {"stars": 300, "id": "main_character", "name_en": "Main Character", "name_he": "שחקנית ראשית", "emoji": "👑", "description_he": "את הכוכבת של הסיפור!"},
]

# App metadata
APP_METADATA = {
    "title": "Ariel's English Adventure",
    "description": "Gamified English learning for kids",
    "version": APP_VERSION,
}
