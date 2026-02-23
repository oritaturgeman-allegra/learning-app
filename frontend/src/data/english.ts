/**
 * English vocabulary data, sentence data, and session planner.
 * Ported from english-data.js + planSession() from english-game.js.
 */

// --- Types ---

export interface VocabWord {
  english: string;
  hebrew: string;
  emoji: string;
  category: string;
}

export interface ScrambleSentence {
  english: string;
  hebrew: string;
}

export interface TrueFalseSentence {
  english: string;
  hebrew: string;
  answer: boolean;
}

export interface SessionPlan {
  game1Words: VocabWord[];
  game2Sentences: ScrambleSentence[];
  game3Words: VocabWord[];
  game4Sentences: TrueFalseSentence[];
}

export interface UnitData {
  name: string;
  nameHebrew: string;
  vocabulary: VocabWord[];
  scrambleSentences: ScrambleSentence[];
  trueFalseSentences: TrueFalseSentence[];
}

// --- Game type map ---

export const GAME_TYPE_MAP: Record<number, string> = {
  1: "word_match",
  2: "sentence_scramble",
  3: "listen_choose",
  4: "true_false",
};

// --- Vocabulary data ---

const UNITS: Record<string, UnitData> = {
  "jet2-unit2": {
    name: "Jet 2: Unit 2",
    nameHebrew: "יחידה 2",
    vocabulary: [
      // Clothes
      { english: "coat", hebrew: "מעיל", emoji: "🧥", category: "clothes" },
      { english: "boots", hebrew: "מגפיים", emoji: "👢", category: "clothes" },
      { english: "dress", hebrew: "שמלה", emoji: "👗", category: "clothes" },
      { english: "shirt", hebrew: "חולצה", emoji: "👕", category: "clothes" },
      { english: "pants", hebrew: "מכנסיים", emoji: "👖", category: "clothes" },
      { english: "shoes", hebrew: "נעליים", emoji: "👟", category: "clothes" },
      { english: "socks", hebrew: "גרביים", emoji: "🧦", category: "clothes" },
      // Seasons
      { english: "winter", hebrew: "חורף", emoji: "❄️", category: "seasons" },
      { english: "spring", hebrew: "אביב", emoji: "🌸", category: "seasons" },
      { english: "summer", hebrew: "קיץ", emoji: "☀️", category: "seasons" },
      { english: "autumn", hebrew: "סתיו", emoji: "🍂", category: "seasons" },
      // Weather
      { english: "warm", hebrew: "חם", emoji: "🌡️", category: "weather" },
      { english: "cold", hebrew: "קר", emoji: "🥶", category: "weather" },
      { english: "sunny", hebrew: "שמשי", emoji: "🌞", category: "weather" },
      { english: "beautiful", hebrew: "יפה", emoji: "✨", category: "weather" },
      // Nature
      { english: "cloud", hebrew: "ענן", emoji: "☁️", category: "nature" },
      { english: "snow", hebrew: "שלג", emoji: "🌨️", category: "nature" },
      { english: "sky", hebrew: "שמיים", emoji: "🌤️", category: "nature" },
      { english: "sun", hebrew: "שמש", emoji: "☀️", category: "nature" },
      { english: "tree", hebrew: "עץ", emoji: "🌳", category: "nature" },
      { english: "park", hebrew: "פארק", emoji: "🏞️", category: "nature" },
      { english: "pool", hebrew: "בריכה", emoji: "🏊", category: "nature" },
      // Actions
      { english: "eat", hebrew: "לאכול", emoji: "🍽️", category: "actions" },
      { english: "sleep", hebrew: "לישון", emoji: "😴", category: "actions" },
      { english: "climb", hebrew: "לטפס", emoji: "🧗", category: "actions" },
      { english: "stand", hebrew: "לעמוד", emoji: "🧍", category: "actions" },
      { english: "play", hebrew: "לשחק", emoji: "🎮", category: "actions" },
      { english: "read a book", hebrew: "לקרוא ספר", emoji: "📖", category: "actions" },
      { english: "play football", hebrew: "לשחק כדורגל", emoji: "⚽", category: "actions" },
      { english: "come", hebrew: "לבוא", emoji: "🚶", category: "actions" },
      { english: "fly a kite", hebrew: "להעיף עפיפון", emoji: "🪁", category: "actions" },
      { english: "make", hebrew: "להכין", emoji: "🔨", category: "actions" },
      { english: "wear", hebrew: "ללבוש", emoji: "👔", category: "actions" },
      // People
      { english: "children", hebrew: "ילדים", emoji: "👧👦", category: "people" },
      { english: "mother", hebrew: "אמא", emoji: "👩", category: "people" },
      { english: "father", hebrew: "אבא", emoji: "👨", category: "people" },
      { english: "they", hebrew: "הם", emoji: "👥", category: "people" },
      { english: "we", hebrew: "אנחנו", emoji: "👫", category: "people" },
      { english: "who", hebrew: "מי", emoji: "❓", category: "people" },
      // Body
      { english: "eyes", hebrew: "עיניים", emoji: "👀", category: "body" },
      { english: "mouth", hebrew: "פה", emoji: "👄", category: "body" },
      { english: "nose", hebrew: "אף", emoji: "👃", category: "body" },
      // Food
      { english: "ice cream", hebrew: "גלידה", emoji: "🍦", category: "food" },
      // Places
      { english: "home", hebrew: "בית", emoji: "🏠", category: "places" },
      { english: "store", hebrew: "חנות", emoji: "🏪", category: "places" },
      { english: "near", hebrew: "קרוב", emoji: "📍", category: "places" },
      // Descriptions
      { english: "funny", hebrew: "מצחיק", emoji: "😂", category: "descriptions" },
      { english: "old", hebrew: "ישן", emoji: "👴", category: "descriptions" },
      { english: "okay", hebrew: "בסדר", emoji: "👌", category: "descriptions" },
      { english: "good for you", hebrew: "טוב בשבילך", emoji: "👍", category: "descriptions" },
      { english: "too", hebrew: "גם", emoji: "➕", category: "descriptions" },
      // Things
      { english: "basketball", hebrew: "כדורסל", emoji: "🏀", category: "things" },
      { english: "game", hebrew: "משחק", emoji: "🎯", category: "things" },
      { english: "picture", hebrew: "תמונה", emoji: "🖼️", category: "things" },
      { english: "wall", hebrew: "קיר", emoji: "🧱", category: "things" },
    ],

    scrambleSentences: [
      { english: "She is wearing a blue dress", hebrew: "היא לובשת שמלה כחולה" },
      { english: "It is cold in winter", hebrew: "קר בחורף" },
      { english: "The sky is sunny today", hebrew: "השמיים שמשיים היום" },
      { english: "I can play basketball", hebrew: "אני יכולה לשחק כדורסל" },
      { english: "I can't fly a kite", hebrew: "אני לא יכולה להעיף עפיפון" },
      { english: "There is a cloud in the sky", hebrew: "יש ענן בשמיים" },
      { english: "He is wearing black boots", hebrew: "הוא נועל מגפיים שחורות" },
      { english: "I want ice cream", hebrew: "אני רוצה גלידה" },
      { english: "They play a funny game", hebrew: "הם משחקים משחק מצחיק" },
      { english: "Come to my home", hebrew: "בואי לבית שלי" },
      { english: "She has beautiful eyes", hebrew: "יש לה עיניים יפות" },
      { english: "The store is near the park", hebrew: "החנות קרובה לפארק" },
      { english: "We make a picture", hebrew: "אנחנו מכינים תמונה" },
      { english: "Who is that old man", hebrew: "מי האיש הזקן הזה" },
      { english: "Father has a new shirt", hebrew: "לאבא יש חולצה חדשה" },
      { english: "My pants are too big", hebrew: "המכנסיים שלי גדולות מדי" },
      { english: "I read a book at home", hebrew: "אני קוראת ספר בבית" },
      { english: "They play football in the park", hebrew: "הם משחקים כדורגל בפארק" },
      { english: "Children eat ice cream in spring", hebrew: "ילדים אוכלים גלידה באביב" },
      { english: "I can climb a tree", hebrew: "אני יכולה לטפס על עץ" },
    ],

    trueFalseSentences: [
      { english: "A coat is warm", hebrew: "מעיל הוא חם", answer: true },
      { english: "We wear boots in summer", hebrew: "אנחנו נועלים מגפיים בקיץ", answer: false },
      { english: "The sun is cold", hebrew: "השמש קרה", answer: false },
      { english: "Children play in the park", hebrew: "ילדים משחקים בפארק", answer: true },
      { english: "Snow is white", hebrew: "שלג הוא לבן", answer: true },
      { english: "We swim in winter", hebrew: "אנחנו שוחים בחורף", answer: false },
      { english: "Trees are green", hebrew: "עצים ירוקים", answer: true },
      { english: "A dress is a food", hebrew: "שמלה היא אוכל", answer: false },
      { english: "Mother is a person", hebrew: "אמא היא אדם", answer: true },
      { english: "Socks go on your head", hebrew: "גרביים הולכים על הראש", answer: false },
      { english: "Basketball is a game", hebrew: "כדורסל הוא משחק", answer: true },
      { english: "Ice cream is hot", hebrew: "גלידה חמה", answer: false },
      { english: "We have two eyes", hebrew: "יש לנו שתי עיניים", answer: true },
      { english: "A nose is on your foot", hebrew: "אף נמצא על הרגל", answer: false },
      { english: "A store is a place", hebrew: "חנות היא מקום", answer: true },
      { english: "A wall can fly", hebrew: "קיר יכול לעוף", answer: false },
      { english: "Shoes go on your feet", hebrew: "נעליים הולכות על הרגליים", answer: true },
      { english: "A mouth is on your hand", hebrew: "פה נמצא על היד", answer: false },
      { english: "You stand on your nose", hebrew: "עומדים על האף", answer: false },
      { english: "We sleep in autumn", hebrew: "אנחנו ישנים בסתיו", answer: true },
      { english: "The pool is good for you", hebrew: "הבריכה טובה בשבילך", answer: true },
      { english: "The game is okay", hebrew: "המשחק בסדר", answer: true },
    ],
  },
};

// --- Utility functions ---

/** Get unit data by session slug (defaults to jet2-unit2) */
export function getUnitData(sessionSlug: string): UnitData {
  return UNITS[sessionSlug] ?? UNITS["jet2-unit2"]!;
}

/** Fisher-Yates shuffle (returns new array) */
export function shuffle<T>(arr: readonly T[]): T[] {
  const copy = [...arr];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j]!, copy[i]!];
  }
  return copy;
}

/** Pick n random unique items from array, optionally excluding one item */
export function pickRandom<T>(arr: readonly T[], n: number, exclude?: T): T[] {
  const filtered = exclude ? arr.filter((item) => item !== exclude) : [...arr];
  return shuffle(filtered).slice(0, n);
}

/** Check if a vocabulary word appears in a sentence */
function wordMatchesSentence(word: string, sentenceWords: string[]): boolean {
  const lower = word.toLowerCase();
  return (
    sentenceWords.includes(lower) ||
    lower.split(" ").every((part) => sentenceWords.includes(part))
  );
}

/** Get vocabulary words covered by a sentence */
export function getWordsInSentence(
  sentence: { english: string },
  vocabulary: readonly VocabWord[],
): string[] {
  const sentenceWords = sentence.english.toLowerCase().split(" ");
  return vocabulary
    .filter((v) => wordMatchesSentence(v.english, sentenceWords))
    .map((v) => v.english.toLowerCase());
}

/** Count how many uncovered words a sentence covers */
function sentenceCoverage(
  sentence: { english: string },
  uncovered: Set<string>,
): number {
  const sentenceWords = sentence.english.toLowerCase().split(" ");
  let count = 0;
  uncovered.forEach((word) => {
    if (wordMatchesSentence(word, sentenceWords)) count++;
  });
  return count;
}

// --- Session planner ---

/**
 * Plan a session: allocate all 55 words across 4 games for full coverage.
 * Uses greedy set-cover algorithm: sentences first, remaining words split between G1 & G3.
 */
export function planSession(
  vocabulary: readonly VocabWord[],
  scrambleSentences: readonly ScrambleSentence[],
  trueFalseSentences: readonly TrueFalseSentence[],
): SessionPlan {
  const uncovered = new Set(vocabulary.map((v) => v.english.toLowerCase()));

  // Greedy pick 6 scramble sentences maximizing coverage
  const g2Available = [...scrambleSentences];
  const g2Selected: ScrambleSentence[] = [];
  for (let i = 0; i < 6; i++) {
    let bestIdx = 0;
    let bestScore = -1;
    g2Available.forEach((s, idx) => {
      const score = sentenceCoverage(s, uncovered);
      if (score > bestScore) {
        bestScore = score;
        bestIdx = idx;
      }
    });
    const picked = g2Available.splice(bestIdx, 1)[0]!;
    g2Selected.push(picked);
    getWordsInSentence(picked, vocabulary).forEach((w) => uncovered.delete(w));
  }

  // Greedy pick 8 true/false sentences maximizing remaining coverage
  const g4Available = [...trueFalseSentences];
  const g4Selected: TrueFalseSentence[] = [];
  for (let i = 0; i < 8; i++) {
    let bestIdx = 0;
    let bestScore = -1;
    g4Available.forEach((s, idx) => {
      const score = sentenceCoverage(s, uncovered);
      if (score > bestScore) {
        bestScore = score;
        bestIdx = idx;
      }
    });
    const picked = g4Available.splice(bestIdx, 1)[0]!;
    g4Selected.push(picked);
    getWordsInSentence(picked, vocabulary).forEach((w) => uncovered.delete(w));
  }

  // Remaining uncovered words go to Games 1 & 3 as direct vocabulary
  const remainingVocab = [...uncovered]
    .map((w) => vocabulary.find((v) => v.english.toLowerCase() === w))
    .filter((v): v is VocabWord => v !== undefined);
  const shuffledRemaining = shuffle(remainingVocab);

  // Split evenly between Game 1 and Game 3
  const half = Math.ceil(shuffledRemaining.length / 2);

  return {
    game1Words: shuffle(shuffledRemaining.slice(0, half)),
    game2Sentences: shuffle(g2Selected),
    game3Words: shuffle(shuffledRemaining.slice(half)),
    game4Sentences: shuffle(g4Selected),
  };
}

/** Validate that a session plan covers all vocabulary words */
export function validateSessionPlan(
  plan: SessionPlan,
  vocabulary: readonly VocabWord[],
): string[] {
  const covered = new Set<string>();

  plan.game1Words.forEach((v) => covered.add(v.english.toLowerCase()));
  plan.game3Words.forEach((v) => covered.add(v.english.toLowerCase()));

  [...plan.game2Sentences, ...plan.game4Sentences].forEach((s) => {
    getWordsInSentence(s, vocabulary).forEach((w) => covered.add(w));
  });

  const allWords = vocabulary.map((v) => v.english.toLowerCase());
  const missing = allWords.filter((w) => !covered.has(w));

  if (missing.length > 0) {
    console.warn("Session plan missing words:", missing);
  }
  return missing;
}
