"""
Static defaults and constants for Ariel Learning App.
"""

from typing import Any, Dict, List

# App version (single source of truth)
APP_VERSION = "2.15.0"

# Recent changelog entries (shown in "What's New" popup)
APP_CHANGELOG: List[Dict[str, str]] = [
    {
        "version": "2.15.0",
        "text": "הגרסה החדשה מתקדמת! עכשיו יש מסכי ניווט אמיתיים עם כוכבים, גביעים וכרטיסי משחק 🌟",
    },
    {
        "version": "2.14.1",
        "text": "השרת מוכן להגיש את הגרסה החדשה! הוספנו API חדש ותמיכה בהרצת React מהשרת 🔧",
    },
    {
        "version": "2.14.0",
        "text": "מתחילים לבנות גרסה חדשה ומודרנית! בקרוב האפליקציה תעבוד מעולה גם בטלפון 📱",
    },
    {
        "version": "2.13.0",
        "text": "שיפור ביצועים! הקוד מסודר יותר וטעינת העמודים מהירה יותר 🚀",
    },
    {
        "version": "2.12.1",
        "text": "רמזים חכמים בכל פרקי החשבון! 💡 לחצי על הנורה ותקבלי עזרה",
    },
]

# Available learning sessions (units), keyed by subject
SESSIONS_BY_SUBJECT: Dict[str, List[Dict[str, Any]]] = {
    "english": [
        {"slug": "jet2-unit2", "name": "Jet 2: Unit 2", "name_he": "ג׳ט 2: יחידה 2", "emoji": "📘"},
    ],
    "math": [
        {"slug": "math-tens-hundreds", "name": "Tens & Hundreds", "name_he": "כפל וחילוק בעשרות ובמאות", "emoji": "🔟"},
        {"slug": "math-two-digit", "name": "Two-Digit Multiply", "name_he": "כפל דו-ספרתי", "emoji": "✖️"},
        {"slug": "math-long-division", "name": "Long Division", "name_he": "חילוק ארוך", "emoji": "➗"},
        {"slug": "math-primes", "name": "Primes & Divisibility", "name_he": "מספרים ראשוניים", "emoji": "🔢"},
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
