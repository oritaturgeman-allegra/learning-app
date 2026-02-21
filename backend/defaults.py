"""
Static defaults and constants for Ariel Learning App.
"""

from typing import Any, Dict, List

# App version (single source of truth)
APP_VERSION = "2.3.0"

# Recent changelog entries (shown in "What's New" popup)
APP_CHANGELOG: List[Dict[str, str]] = [
    {
        "version": "2.3.0",
        "text": "Getting ready for math! New subject-based URLs — English lives at /learning/english/ now",
    },
    {
        "version": "2.2.0",
        "text": "Choose your learning session! New session picker screen — pick a unit and jump straight to the games",
    },
    {
        "version": "2.1.0",
        "text": "Refresh without losing your place! The game menu now has its own page — no more starting over",
    },
]

# Available learning sessions (units)
SESSIONS: List[Dict[str, str]] = [
    {"slug": "jet2-unit2", "name": "Jet 2: Unit 2", "name_he": "ג׳ט 2: יחידה 2", "emoji": "📘"},
]

# Valid session slugs for route validation
VALID_SESSION_SLUGS: set = {s["slug"] for s in SESSIONS}

# Valid subjects for route validation
VALID_SUBJECTS: set = {"english"}

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
    "title": "Ariel Learning App",
    "description": "Gamified English learning for kids",
    "version": APP_VERSION,
}
