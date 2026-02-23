/**
 * Reward orchestration hook — milestone checks, reward unlocks, confetti.
 *
 * Timing:
 * 1. Stars update → checkMilestone() called
 * 2. 0ms: Milestone overlay opens + confetti + celebration audio
 * 3. 2500-3000ms: Milestone auto-closes
 * 4. 3000ms: Reward popup opens (if new tier unlocked) + more confetti
 * 5. 8000ms: Reward popup auto-closes
 */

import { useCallback, useRef, useState } from "react";
import { playCelebration } from "@/hooks/useAudio";
import type { RewardTier } from "@/api/types";

const LS_LAST_MILESTONE = "ariel_last_milestone";
const LS_EARNED_REWARDS = "ariel_earned_rewards";

function getLastMilestone(): number {
  return parseInt(localStorage.getItem(LS_LAST_MILESTONE) || "0", 10);
}

function getEarnedRewardIds(): string[] {
  try {
    return JSON.parse(localStorage.getItem(LS_EARNED_REWARDS) || "[]") as string[];
  } catch {
    return [];
  }
}

export interface UseRewardsReturn {
  // Milestone state
  milestoneOpen: boolean;
  milestoneStars: number;
  isParade: boolean;
  closeMilestone: () => void;

  // Reward popup state
  rewardPopupOpen: boolean;
  rewardTier: RewardTier | null;
  closeReward: () => void;

  // Confetti
  confettiActive: boolean;

  // Trigger
  checkMilestone: (totalStars: number, rewardTiers: RewardTier[]) => void;
}

export function useRewards(): UseRewardsReturn {
  const [milestoneOpen, setMilestoneOpen] = useState(false);
  const [milestoneStars, setMilestoneStars] = useState(0);
  const [isParade, setIsParade] = useState(false);
  const [rewardPopupOpen, setRewardPopupOpen] = useState(false);
  const [rewardTier, setRewardTier] = useState<RewardTier | null>(null);
  const [confettiActive, setConfettiActive] = useState(false);

  // Prevent re-entrance during animation sequence
  const animatingRef = useRef(false);

  const triggerConfetti = useCallback(() => {
    setConfettiActive(false);
    // Force re-render with new pieces by toggling off then on
    requestAnimationFrame(() => setConfettiActive(true));
  }, []);

  const closeMilestone = useCallback(() => {
    setMilestoneOpen(false);
  }, []);

  const closeReward = useCallback(() => {
    setRewardPopupOpen(false);
    setRewardTier(null);
    animatingRef.current = false;
  }, []);

  const checkMilestone = useCallback(
    (totalStars: number, rewardTiers: RewardTier[]) => {
      if (animatingRef.current) return;

      const lastMilestone = getLastMilestone();
      const currentMilestone = Math.floor(totalStars / 5) * 5;

      if (currentMilestone <= lastMilestone || currentMilestone <= 0) {
        // No new milestone, but still check for reward unlock
        checkRewardOnly(totalStars, rewardTiers);
        return;
      }

      animatingRef.current = true;

      // Save new milestone
      localStorage.setItem(LS_LAST_MILESTONE, currentMilestone.toString());

      // Determine type
      const parade = totalStars >= 10 && currentMilestone % 10 === 0;
      setIsParade(parade);
      setMilestoneStars(totalStars);
      setMilestoneOpen(true);
      triggerConfetti();
      playCelebration();

      // After milestone animation, check for reward unlock
      setTimeout(() => {
        setMilestoneOpen(false);
        checkRewardUnlock(totalStars, rewardTiers);
      }, parade ? 3000 : 2500);
    },
    [triggerConfetti],
  );

  function checkRewardOnly(totalStars: number, rewardTiers: RewardTier[]): void {
    const earned = getEarnedRewardIds();
    const newTier = rewardTiers.find(
      (t) => t.stars <= totalStars && !earned.includes(t.id),
    );
    if (newTier) {
      earned.push(newTier.id);
      localStorage.setItem(LS_EARNED_REWARDS, JSON.stringify(earned));
      animatingRef.current = true;
      setRewardTier(newTier);
      setRewardPopupOpen(true);
      triggerConfetti();
      playCelebration();
    }
  }

  function checkRewardUnlock(totalStars: number, rewardTiers: RewardTier[]): void {
    const earned = getEarnedRewardIds();
    const newTier = rewardTiers.find(
      (t) => t.stars <= totalStars && !earned.includes(t.id),
    );
    if (newTier) {
      earned.push(newTier.id);
      localStorage.setItem(LS_EARNED_REWARDS, JSON.stringify(earned));
      // Show reward popup after short delay (3s after milestone started)
      setTimeout(() => {
        setRewardTier(newTier);
        setRewardPopupOpen(true);
        triggerConfetti();
        playCelebration();
      }, 500);
    } else {
      animatingRef.current = false;
    }
  }

  return {
    milestoneOpen,
    milestoneStars,
    isParade,
    closeMilestone,
    rewardPopupOpen,
    rewardTier,
    closeReward,
    confettiActive,
    checkMilestone,
  };
}
