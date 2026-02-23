/**
 * App-wide context providing progress and config data.
 * Fetches from API on mount, falls back to localStorage for instant display.
 */

import { createContext, useContext, useEffect, useState, useCallback, type ReactNode } from "react";
import { loadConfig, loadProgress } from "@/api/game";
import type { RewardTier, Session, Topic } from "@/api/types";

// --- Context shape ---

interface AppContextValue {
  // Progress
  totalStars: number;
  starsBySession: Record<string, number>;
  completedSessions: string[];
  earnedRewards: string[];
  nextReward: RewardTier | null;

  // Config
  rewardTiers: RewardTier[];
  sessionsBySubject: Record<string, Session[]>;
  topicsBySubject: Record<string, Topic[]>;
  appVersion: string;

  // State
  loading: boolean;
  refreshProgress: () => Promise<void>;

  // Actions
  awardStars: (count: number) => void;
}

const AppContext = createContext<AppContextValue | null>(null);

// --- localStorage keys (backward-compatible with legacy app) ---

const LS_STARS = "ariel_stars";
const LS_REWARDS = "ariel_earned_rewards";

function readLocalStars(): number {
  return parseInt(localStorage.getItem(LS_STARS) || "0", 10);
}

function readLocalRewards(): string[] {
  try {
    return JSON.parse(localStorage.getItem(LS_REWARDS) || "[]") as string[];
  } catch {
    return [];
  }
}

// --- Provider ---

export function AppProvider({ children }: { children: ReactNode }) {
  const [totalStars, setTotalStars] = useState(readLocalStars);
  const [starsBySession, setStarsBySession] = useState<Record<string, number>>({});
  const [completedSessions, setCompletedSessions] = useState<string[]>([]);
  const [earnedRewards, setEarnedRewards] = useState<string[]>(readLocalRewards);
  const [nextReward, setNextReward] = useState<RewardTier | null>(null);
  const [rewardTiers, setRewardTiers] = useState<RewardTier[]>([]);
  const [sessionsBySubject, setSessionsBySubject] = useState<Record<string, Session[]>>({});
  const [topicsBySubject, setTopicsBySubject] = useState<Record<string, Topic[]>>({});
  const [appVersion, setAppVersion] = useState("");
  const [loading, setLoading] = useState(true);

  // Optimistically update stars locally (for immediate UI feedback)
  const awardStars = useCallback((count: number) => {
    setTotalStars((prev) => {
      const newTotal = prev + count;
      localStorage.setItem(LS_STARS, String(newTotal));
      return newTotal;
    });
  }, []);

  const refreshProgress = useCallback(async () => {
    try {
      const res = await loadProgress();
      if (res.success) {
        const d = res.data;
        setTotalStars(d.total_stars);
        setStarsBySession(d.stars_by_session);
        setCompletedSessions(d.completed_sessions);
        setEarnedRewards(d.earned_rewards);
        setNextReward(d.next_reward);

        // Sync to localStorage for backward compatibility
        localStorage.setItem(LS_STARS, String(d.total_stars));
        localStorage.setItem(LS_REWARDS, JSON.stringify(d.earned_rewards));
      }
    } catch (err) {
      console.error("Failed to load progress:", err);
    }
  }, []);

  // Load config + progress on mount
  useEffect(() => {
    async function init() {
      try {
        const [configRes] = await Promise.all([loadConfig(), refreshProgress()]);
        if (configRes.success) {
          const c = configRes.data;
          setRewardTiers(c.reward_tiers);
          setSessionsBySubject(c.sessions_by_subject);
          setTopicsBySubject(c.topics_by_subject || {});
          setAppVersion(c.version);
        }
      } catch (err) {
        console.error("Failed to load app data:", err);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, [refreshProgress]);

  return (
    <AppContext.Provider
      value={{
        totalStars,
        starsBySession,
        completedSessions,
        earnedRewards,
        nextReward,
        rewardTiers,
        sessionsBySubject,
        topicsBySubject,
        appVersion,
        loading,
        refreshProgress,
        awardStars,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

// --- Hook ---

export function useApp(): AppContextValue {
  const ctx = useContext(AppContext);
  if (!ctx) {
    throw new Error("useApp must be used within AppProvider");
  }
  return ctx;
}
