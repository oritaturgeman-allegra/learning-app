/**
 * TypeScript interfaces for API responses.
 * Matches exact shapes returned by backend/routes/game.py.
 */

// --- Shared types ---

export interface Session {
  slug: string;
  name: string;
  name_he: string;
  emoji: string;
}

export interface RewardTier {
  stars: number;
  id: string;
  name_en: string;
  name_he: string;
  emoji: string;
  description_he: string;
}

export interface ChangelogEntry {
  version: string;
  text: string;
}

// --- API response wrapper ---

export interface ApiResponse<T> {
  success: boolean;
  data: T;
}

// --- /api/game/config ---

export interface ConfigData {
  version: string;
  changelog: ChangelogEntry[];
  reward_tiers: RewardTier[];
  sessions: Session[] | Record<string, Session[]>;
  sessions_by_subject: Record<string, Session[]>;
  subject: string | null;
  session_slug: string | null;
}

// --- /api/game/progress ---

export interface GameAccuracy {
  games_played: number;
  average_accuracy: number;
  total_stars: number;
}

export interface WeakWord {
  word: string;
  accuracy: number;
  attempts: number;
}

export interface ProgressData {
  total_stars: number;
  games_played: number;
  accuracy_by_game: Record<string, GameAccuracy>;
  stars_by_session: Record<string, number>;
  completed_sessions: string[];
  weak_words: WeakWord[];
  recent_games: Record<string, unknown>[];
  earned_rewards: string[];
  next_reward: RewardTier | null;
}

// --- /api/game/result ---

export interface WordResult {
  word: string;
  correct: boolean;
  category?: string;
}

export interface GameResultRequest {
  game_type: string;
  score: number;
  max_score: number;
  word_results?: WordResult[];
  session_slug?: string;
}

export interface GameResultData {
  id: number;
  category: string;
  game_type: string;
  score: number;
  max_score: number;
  accuracy: number;
  word_results: WordResult[];
  session_slug: string | null;
  played_at: string;
}

// --- /api/game/practiced-words ---

export interface PracticedWordsData {
  practiced_words: string[];
}

// --- /api/game/reset ---

export interface ResetData {
  reset_at: string;
}
