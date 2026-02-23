/**
 * Game 4: Bubble Pop — פוצצי בועות!
 *
 * 8 rounds, 1 star per correct bubble popped.
 * Shows a target number and 6 bubbles (2-3 correct + 3-4 wrong expressions).
 * Multiple taps per round — does NOT use useGameEngine.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Box, LinearProgress, Typography } from "@mui/material";
import { playCorrect, playWrong } from "@/hooks/useAudio";
import { useApp } from "@/context/AppContext";
import { generateBubbles } from "@/data/math";
import type { BubbleItem } from "@/data/math";
import type { WordResult } from "@/api/types";

interface BubblePopProps {
  sessionSlug: string;
  onFinish: (score: number, maxScore: number, wordResults: WordResult[]) => void;
}

const TOTAL_ROUNDS = 8;

// Bubble colors — cycled per bubble
const BUBBLE_COLORS = [
  "#93c5fd", "#a5b4fc", "#c4b5fd", "#f9a8d4", "#fda4af", "#fdba74",
];

interface RoundData {
  target: number;
  bubbles: (BubbleItem & { popped: boolean; shaking: boolean })[];
  correctCount: number;
}

export default function BubblePop({ sessionSlug, onFinish }: BubblePopProps) {
  const { awardStars } = useApp();
  const [currentRound, setCurrentRound] = useState(0);
  const [gameScore, setGameScore] = useState(0);
  const [isFinished, setIsFinished] = useState(false);
  const wordResultsRef = useRef<WordResult[]>([]);
  const [foundCount, setFoundCount] = useState(0);
  const advancingRef = useRef(false);

  // Generate all rounds upfront
  const rounds = useMemo(
    () =>
      Array.from({ length: TOTAL_ROUNDS }, () => {
        const { target, bubbles, correctCount } = generateBubbles(sessionSlug);
        return {
          target,
          bubbles: bubbles.map((b) => ({ ...b, popped: false, shaking: false })),
          correctCount,
        } as RoundData;
      }),
    [sessionSlug],
  );

  const [roundBubbles, setRoundBubbles] = useState(rounds[0]!.bubbles);
  const round = rounds[currentRound]!;

  // Sync bubbles on round change
  useEffect(() => {
    setRoundBubbles(rounds[currentRound]!.bubbles);
    setFoundCount(0);
    advancingRef.current = false;
  }, [currentRound, rounds]);

  // Count max possible stars across all rounds
  const maxScore = useMemo(
    () => rounds.reduce((sum, r) => sum + r.correctCount, 0),
    [rounds],
  );

  const progressPercent = ((currentRound + (isFinished ? 1 : 0)) / TOTAL_ROUNDS) * 100;

  const advanceRound = useCallback(() => {
    if (advancingRef.current) return;
    advancingRef.current = true;
    setTimeout(() => {
      const next = currentRound + 1;
      if (next >= TOTAL_ROUNDS) {
        setIsFinished(true);
      } else {
        setCurrentRound(next);
      }
    }, 1500);
  }, [currentRound]);

  const handleBubbleClick = (index: number) => {
    if (isFinished || advancingRef.current) return;
    const bubble = roundBubbles[index]!;
    if (bubble.popped) return;

    if (bubble.isCorrect) {
      playCorrect();
      awardStars(1);
      setGameScore((prev) => prev + 1);

      const newBubbles = roundBubbles.map((b, i) =>
        i === index ? { ...b, popped: true } : b,
      );
      setRoundBubbles(newBubbles);

      wordResultsRef.current.push({
        word: `${round.target} = ${bubble.expression}`,
        correct: true,
        category: "bubble_pop",
      });

      const newFound = foundCount + 1;
      setFoundCount(newFound);

      // All correct bubbles found — advance
      if (newFound >= round.correctCount) {
        advanceRound();
      }
    } else {
      playWrong();

      wordResultsRef.current.push({
        word: `${round.target} ≠ ${bubble.expression}`,
        correct: false,
        category: "bubble_pop",
      });

      // Shake animation
      const newBubbles = roundBubbles.map((b, i) =>
        i === index ? { ...b, shaking: true } : b,
      );
      setRoundBubbles(newBubbles);
      setTimeout(() => {
        setRoundBubbles((prev) =>
          prev.map((b, i) => (i === index ? { ...b, shaking: false } : b)),
        );
      }, 500);
    }
  };

  // Trigger onFinish
  if (isFinished) {
    setTimeout(
      () => onFinish(gameScore, maxScore, wordResultsRef.current),
      0,
    );
    return null;
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", px: 2, py: 3, gap: 3 }}>
      {/* Progress bar */}
      <Box sx={{ width: "100%", maxWidth: 500 }}>
        <LinearProgress
          variant="determinate"
          value={progressPercent}
          sx={{
            height: 8,
            borderRadius: 4,
            bgcolor: "rgba(0,0,0,0.08)",
            "& .MuiLinearProgress-bar": {
              borderRadius: 4,
              background: "linear-gradient(90deg, #c4b5fd, #8b5cf6)",
            },
          }}
        />
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ display: "block", textAlign: "center", mt: 0.5 }}
        >
          {currentRound + 1} / {TOTAL_ROUNDS}
        </Typography>
      </Box>

      {/* Target number */}
      <Box
        sx={{
          bgcolor: "white",
          borderRadius: 4,
          px: 4,
          py: 2,
          boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
          textAlign: "center",
          animation: "popIn 0.3s ease-out",
        }}
      >
        <Typography
          sx={{
            fontFamily: "'Rubik', sans-serif",
            fontSize: "0.9rem",
            color: "text.secondary",
            mb: 0.5,
          }}
        >
          מצאי את התרגילים ששווים
        </Typography>
        <Typography
          sx={{
            fontFamily: "'Fredoka', sans-serif",
            fontWeight: 700,
            fontSize: { xs: "2.5rem", sm: "3rem" },
            color: "#7c3aed",
            direction: "ltr",
          }}
        >
          {round.target}
        </Typography>
        <Typography
          sx={{
            fontFamily: "'Rubik', sans-serif",
            fontSize: "0.85rem",
            color: "text.secondary",
          }}
        >
          {foundCount} / {round.correctCount} נמצאו
        </Typography>
      </Box>

      {/* Bubble grid */}
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: { xs: 1.5, sm: 2 },
          width: "100%",
          maxWidth: 400,
        }}
      >
        {roundBubbles.map((bubble, i) => (
          <Box
            key={`${currentRound}-${i}`}
            onClick={() => handleBubbleClick(i)}
            sx={{
              width: "100%",
              aspectRatio: "1",
              borderRadius: "50%",
              bgcolor: bubble.popped ? "#dcfce7" : BUBBLE_COLORS[i % BUBBLE_COLORS.length],
              border: bubble.popped ? "3px solid #22c55e" : "3px solid rgba(255,255,255,0.5)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: bubble.popped ? "default" : "pointer",
              transition: "transform 0.2s, opacity 0.3s",
              opacity: bubble.popped ? 0.6 : 1,
              transform: bubble.popped ? "scale(0.85)" : "scale(1)",
              animation: bubble.shaking
                ? "shake 0.5s ease-in-out"
                : bubble.popped
                  ? "none"
                  : `float ${2 + (i % 3) * 0.5}s ease-in-out infinite`,
              "&:hover": {
                transform: bubble.popped ? "scale(0.85)" : "scale(1.08)",
              },
              "&:active": {
                transform: bubble.popped ? "scale(0.85)" : "scale(0.95)",
              },
              boxShadow: bubble.popped
                ? "none"
                : "0 4px 12px rgba(0,0,0,0.15)",
            }}
          >
            <Typography
              sx={{
                fontFamily: "'Fredoka', sans-serif",
                fontWeight: 600,
                fontSize: { xs: "0.85rem", sm: "1rem" },
                color: bubble.popped ? "#22c55e" : "white",
                textAlign: "center",
                direction: "ltr",
                lineHeight: 1.2,
                px: 0.5,
                textDecoration: bubble.popped ? "line-through" : "none",
              }}
            >
              {bubble.expression}
            </Typography>
          </Box>
        ))}
      </Box>
    </Box>
  );
}
