/**
 * Static game card metadata per subject.
 * Colors match legacy CSS classes from english.css and math.css.
 */

export interface GameInfo {
  id: number;
  type: string;
  title: string;
  desc: string;
  emoji: string;
  color: string;
}

export const ENGLISH_GAMES: GameInfo[] = [
  { id: 1, type: "word_match", title: "מה המילה?", desc: "התאימי את המילה באנגלית", emoji: "🔤", color: "#c4b5fd" },
  { id: 2, type: "sentence_scramble", title: "תרגמי את המשפט", desc: "סדרי את המילים בסדר הנכון", emoji: "📝", color: "#fdba74" },
  { id: 3, type: "listen_choose", title: "האזיני ובחרי", desc: "שמעי את המילה ובחרי תמונה", emoji: "🔊", color: "#7dd3fc" },
  { id: 4, type: "true_false", title: "נכון או לא?", desc: "האם המשפט נכון?", emoji: "🤔", color: "#f9a8d4" },
];

export const MATH_GAMES: GameInfo[] = [
  { id: 1, type: "quick_solve", title: "פתרי מהר!", desc: "בחרי את התשובה הנכונה", emoji: "⚡", color: "#93c5fd" },
  { id: 2, type: "missing_number", title: "מצאי את המספר!", desc: "מצאי את המספר החסר", emoji: "🔍", color: "#6ee7b7" },
  { id: 3, type: "true_false_math", title: "נכון או לא?", desc: "האם התרגיל נכון?", emoji: "🤔", color: "#fda4af" },
  { id: 4, type: "bubble_pop", title: "פוצצי בועות!", desc: "פוצצי בועות שוות למספר", emoji: "🫧", color: "#c4b5fd" },
];

export const GAMES_BY_SUBJECT: Record<string, GameInfo[]> = {
  english: ENGLISH_GAMES,
  math: MATH_GAMES,
};
