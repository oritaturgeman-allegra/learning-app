"""
Static defaults and constants for Ariel Learning App.
"""

from typing import Any, Dict, List

# App version (single source of truth)
APP_VERSION = "2.6.0"

# Recent changelog entries (shown in "What's New" popup)
APP_CHANGELOG: List[Dict[str, str]] = [
    {
        "version": "2.6.0",
        "text": "הכוכבים שלך לכל נושא! כל יחידה מציגה כמה כוכבים צברת בה",
    },
    {
        "version": "2.5.0",
        "text": "חשבון is here! Switch between English and Math from any screen — Math games coming soon",
    },
    {
        "version": "2.4.0",
        "text": "Pick your subject first! New subject picker screen — choose English or Math then pick your unit",
    },
]

# Available learning sessions (units), keyed by subject
SESSIONS_BY_SUBJECT: Dict[str, List[Dict[str, Any]]] = {
    "english": [
        {"slug": "jet2-unit2", "name": "Jet 2: Unit 2", "name_he": "ג׳ט 2: יחידה 2", "emoji": "📘"},
    ],
    "math": [
        {"slug": "multiply-divide", "name": "Multiply & Divide", "name_he": "כפל וחילוק", "emoji": "✖️", "locked": True},
    ],
}

# Flat list of all sessions (for backward compat)
SESSIONS: List[Dict[str, Any]] = [s for sessions in SESSIONS_BY_SUBJECT.values() for s in sessions]

# Valid session slugs for route validation
VALID_SESSION_SLUGS: set = {s["slug"] for s in SESSIONS}

# Valid subjects for route validation
VALID_SUBJECTS: set = set(SESSIONS_BY_SUBJECT.keys())

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
