/**
 * Shared game engine hook — manages round progression, scoring,
 * answer feedback, and word result accumulation for all 4 English games.
 */

import { useState, useRef, useCallback } from "react";
import { playCorrect, playWrong } from "@/hooks/useAudio";
import { useApp } from "@/context/AppContext";
import type { WordResult } from "@/api/types";

// --- Types ---

export interface UseGameEngineOptions {
  totalRounds: number;
  starsPerCorrect: number; // 1 for most games, 2 for sentence_scramble
  answerDelay: number; // ms to wait after answer before advancing (1500 or 2500)
}

export interface UseGameEngineReturn {
  currentRound: number;
  totalRounds: number;
  gameScore: number;
  maxScore: number;
  isAnswering: boolean;
  isFinished: boolean;
  progressPercent: number;
  wordResults: WordResult[];
  submitAnswer: (correct: boolean, results: WordResult[]) => void;
}

// --- Hook ---

export function useGameEngine(options: UseGameEngineOptions): UseGameEngineReturn {
  const { totalRounds, starsPerCorrect, answerDelay } = options;
  const { awardStars } = useApp();

  const [currentRound, setCurrentRound] = useState(0);
  const [gameScore, setGameScore] = useState(0);
  const [isAnswering, setIsAnswering] = useState(false);
  const [isFinished, setIsFinished] = useState(false);
  const wordResultsRef = useRef<WordResult[]>([]);
  const [wordResults, setWordResults] = useState<WordResult[]>([]);

  const maxScore = totalRounds * starsPerCorrect;
  const progressPercent = totalRounds > 0 ? ((currentRound + (isFinished ? 1 : 0)) / totalRounds) * 100 : 0;

  const submitAnswer = useCallback(
    (correct: boolean, results: WordResult[]) => {
      if (isAnswering || isFinished) return;

      // Audio feedback
      if (correct) {
        playCorrect();
        awardStars(starsPerCorrect);
        setGameScore((prev) => prev + starsPerCorrect);
      } else {
        playWrong();
      }

      // Accumulate word results
      wordResultsRef.current = [...wordResultsRef.current, ...results];
      setWordResults([...wordResultsRef.current]);

      // Lock input during delay
      setIsAnswering(true);

      // Advance after delay
      setTimeout(() => {
        setIsAnswering(false);
        const nextRound = currentRound + 1;
        if (nextRound >= totalRounds) {
          setIsFinished(true);
        } else {
          setCurrentRound(nextRound);
        }
      }, answerDelay);
    },
    [isAnswering, isFinished, currentRound, totalRounds, starsPerCorrect, answerDelay, awardStars],
  );

  return {
    currentRound,
    totalRounds,
    gameScore,
    maxScore,
    isAnswering,
    isFinished,
    progressPercent,
    wordResults,
    submitAnswer,
  };
}
