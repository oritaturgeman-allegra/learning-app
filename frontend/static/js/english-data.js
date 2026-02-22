/**
 * english-data.js — English vocabulary data and config constants.
 * Loaded after shared.js; before english-game.js.
 */

/* ==========================================================================
   VOCABULARY DATA — Organized by textbook unit
   ========================================================================== */
const UNITS = {
    'jet2-unit2': {
        name: 'Jet 2: Unit 2',
        nameHebrew: 'יחידה 2',

        vocabulary: [
            // --- Clothes ---
            { english: 'coat', hebrew: 'מעיל', emoji: '🧥', category: 'clothes' },
            { english: 'boots', hebrew: 'מגפיים', emoji: '👢', category: 'clothes' },
            { english: 'dress', hebrew: 'שמלה', emoji: '👗', category: 'clothes' },
            { english: 'shirt', hebrew: 'חולצה', emoji: '👕', category: 'clothes' },
            { english: 'pants', hebrew: 'מכנסיים', emoji: '👖', category: 'clothes' },
            { english: 'shoes', hebrew: 'נעליים', emoji: '👟', category: 'clothes' },
            { english: 'socks', hebrew: 'גרביים', emoji: '🧦', category: 'clothes' },
            // --- Seasons ---
            { english: 'winter', hebrew: 'חורף', emoji: '❄️', category: 'seasons' },
            { english: 'spring', hebrew: 'אביב', emoji: '🌸', category: 'seasons' },
            { english: 'summer', hebrew: 'קיץ', emoji: '☀️', category: 'seasons' },
            { english: 'autumn', hebrew: 'סתיו', emoji: '🍂', category: 'seasons' },
            // --- Weather ---
            { english: 'warm', hebrew: 'חם', emoji: '🌡️', category: 'weather' },
            { english: 'cold', hebrew: 'קר', emoji: '🥶', category: 'weather' },
            { english: 'sunny', hebrew: 'שמשי', emoji: '🌞', category: 'weather' },
            { english: 'beautiful', hebrew: 'יפה', emoji: '✨', category: 'weather' },
            // --- Nature ---
            { english: 'cloud', hebrew: 'ענן', emoji: '☁️', category: 'nature' },
            { english: 'snow', hebrew: 'שלג', emoji: '🌨️', category: 'nature' },
            { english: 'sky', hebrew: 'שמיים', emoji: '🌤️', category: 'nature' },
            { english: 'sun', hebrew: 'שמש', emoji: '☀️', category: 'nature' },
            { english: 'tree', hebrew: 'עץ', emoji: '🌳', category: 'nature' },
            { english: 'park', hebrew: 'פארק', emoji: '🏞️', category: 'nature' },
            { english: 'pool', hebrew: 'בריכה', emoji: '🏊', category: 'nature' },
            // --- Actions ---
            { english: 'eat', hebrew: 'לאכול', emoji: '🍽️', category: 'actions' },
            { english: 'sleep', hebrew: 'לישון', emoji: '😴', category: 'actions' },
            { english: 'climb', hebrew: 'לטפס', emoji: '🧗', category: 'actions' },
            { english: 'stand', hebrew: 'לעמוד', emoji: '🧍', category: 'actions' },
            { english: 'play', hebrew: 'לשחק', emoji: '🎮', category: 'actions' },
            { english: 'read a book', hebrew: 'לקרוא ספר', emoji: '📖', category: 'actions' },
            { english: 'play football', hebrew: 'לשחק כדורגל', emoji: '⚽', category: 'actions' },
            { english: 'come', hebrew: 'לבוא', emoji: '🚶', category: 'actions' },
            { english: 'fly a kite', hebrew: 'להעיף עפיפון', emoji: '🪁', category: 'actions' },
            { english: 'make', hebrew: 'להכין', emoji: '🔨', category: 'actions' },
            { english: 'wear', hebrew: 'ללבוש', emoji: '👔', category: 'actions' },
            // --- People ---
            { english: 'children', hebrew: 'ילדים', emoji: '👧👦', category: 'people' },
            { english: 'mother', hebrew: 'אמא', emoji: '👩', category: 'people' },
            { english: 'father', hebrew: 'אבא', emoji: '👨', category: 'people' },
            { english: 'they', hebrew: 'הם', emoji: '👥', category: 'people' },
            { english: 'we', hebrew: 'אנחנו', emoji: '👫', category: 'people' },
            { english: 'who', hebrew: 'מי', emoji: '❓', category: 'people' },
            // --- Body ---
            { english: 'eyes', hebrew: 'עיניים', emoji: '👀', category: 'body' },
            { english: 'mouth', hebrew: 'פה', emoji: '👄', category: 'body' },
            { english: 'nose', hebrew: 'אף', emoji: '👃', category: 'body' },
            // --- Food ---
            { english: 'ice cream', hebrew: 'גלידה', emoji: '🍦', category: 'food' },
            // --- Places ---
            { english: 'home', hebrew: 'בית', emoji: '🏠', category: 'places' },
            { english: 'store', hebrew: 'חנות', emoji: '🏪', category: 'places' },
            { english: 'near', hebrew: 'קרוב', emoji: '📍', category: 'places' },
            // --- Descriptions ---
            { english: 'funny', hebrew: 'מצחיק', emoji: '😂', category: 'descriptions' },
            { english: 'old', hebrew: 'ישן', emoji: '👴', category: 'descriptions' },
            { english: 'okay', hebrew: 'בסדר', emoji: '👌', category: 'descriptions' },
            { english: 'good for you', hebrew: 'טוב בשבילך', emoji: '👍', category: 'descriptions' },
            { english: 'too', hebrew: 'גם', emoji: '➕', category: 'descriptions' },
            // --- Things ---
            { english: 'basketball', hebrew: 'כדורסל', emoji: '🏀', category: 'things' },
            { english: 'game', hebrew: 'משחק', emoji: '🎯', category: 'things' },
            { english: 'picture', hebrew: 'תמונה', emoji: '🖼️', category: 'things' },
            { english: 'wall', hebrew: 'קיר', emoji: '🧱', category: 'things' },
        ],

        scrambleSentences: [
            { english: 'She is wearing a blue dress', hebrew: 'היא לובשת שמלה כחולה' },
            { english: 'It is cold in winter', hebrew: 'קר בחורף' },
            { english: 'The sky is sunny today', hebrew: 'השמיים שמשיים היום' },
            { english: 'I can play basketball', hebrew: 'אני יכולה לשחק כדורסל' },
            { english: "I can't fly a kite", hebrew: 'אני לא יכולה להעיף עפיפון' },
            { english: 'There is a cloud in the sky', hebrew: 'יש ענן בשמיים' },
            { english: 'He is wearing black boots', hebrew: 'הוא נועל מגפיים שחורות' },
            { english: 'I want ice cream', hebrew: 'אני רוצה גלידה' },
            { english: 'They play a funny game', hebrew: 'הם משחקים משחק מצחיק' },
            { english: 'Come to my home', hebrew: 'בואי לבית שלי' },
            { english: 'She has beautiful eyes', hebrew: 'יש לה עיניים יפות' },
            { english: 'The store is near the park', hebrew: 'החנות קרובה לפארק' },
            { english: 'We make a picture', hebrew: 'אנחנו מכינים תמונה' },
            { english: 'Who is that old man', hebrew: 'מי האיש הזקן הזה' },
            { english: 'Father has a new shirt', hebrew: 'לאבא יש חולצה חדשה' },
            { english: 'My pants are too big', hebrew: 'המכנסיים שלי גדולות מדי' },
            { english: 'I read a book at home', hebrew: 'אני קוראת ספר בבית' },
            { english: 'They play football in the park', hebrew: 'הם משחקים כדורגל בפארק' },
            { english: 'Children eat ice cream in spring', hebrew: 'ילדים אוכלים גלידה באביב' },
            { english: 'I can climb a tree', hebrew: 'אני יכולה לטפס על עץ' },
        ],

        trueFalseSentences: [
            { english: 'A coat is warm', hebrew: 'מעיל הוא חם', answer: true },
            { english: 'We wear boots in summer', hebrew: 'אנחנו נועלים מגפיים בקיץ', answer: false },
            { english: 'The sun is cold', hebrew: 'השמש קרה', answer: false },
            { english: 'Children play in the park', hebrew: 'ילדים משחקים בפארק', answer: true },
            { english: 'Snow is white', hebrew: 'שלג הוא לבן', answer: true },
            { english: 'We swim in winter', hebrew: 'אנחנו שוחים בחורף', answer: false },
            { english: 'Trees are green', hebrew: 'עצים ירוקים', answer: true },
            { english: 'A dress is a food', hebrew: 'שמלה היא אוכל', answer: false },
            { english: 'Mother is a person', hebrew: 'אמא היא אדם', answer: true },
            { english: 'Socks go on your head', hebrew: 'גרביים הולכים על הראש', answer: false },
            { english: 'Basketball is a game', hebrew: 'כדורסל הוא משחק', answer: true },
            { english: 'Ice cream is hot', hebrew: 'גלידה חמה', answer: false },
            { english: 'We have two eyes', hebrew: 'יש לנו שתי עיניים', answer: true },
            { english: 'A nose is on your foot', hebrew: 'אף נמצא על הרגל', answer: false },
            { english: 'A store is a place', hebrew: 'חנות היא מקום', answer: true },
            { english: 'A wall can fly', hebrew: 'קיר יכול לעוף', answer: false },
            { english: 'Shoes go on your feet', hebrew: 'נעליים הולכות על הרגליים', answer: true },
            { english: 'A mouth is on your hand', hebrew: 'פה נמצא על היד', answer: false },
            { english: 'You stand on your nose', hebrew: 'עומדים על האף', answer: false },
            { english: 'We sleep in autumn', hebrew: 'אנחנו ישנים בסתיו', answer: true },
            { english: 'The pool is good for you', hebrew: 'הבריכה טובה בשבילך', answer: true },
            { english: 'The game is okay', hebrew: 'המשחק בסדר', answer: true },
        ],
    },
};

/** Map game number to game_type string */
const GAME_TYPE_MAP = {
    1: 'word_match',
    2: 'sentence_scramble',
    3: 'listen_choose',
    4: 'true_false',
};
