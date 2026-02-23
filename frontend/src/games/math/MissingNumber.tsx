/**
 * Game 2: Missing Number — מצאי את המספר!
 *
 * 8 rounds, 1 star per correct answer.
 * Blanks a number from the equation, shows 4 multiple-choice options.
 */

import { useMemo, useState } from "react";
import { Box, Button, LinearProgress, Typography } from "@mui/material";
import { useGameEngine } from "@/hooks/useGameEngine";
import { generateMissingNumberProblem, generateDistractors } from "@/data/math";
import { shuffle } from "@/data/english";
import type { MissingNumberProblem } from "@/data/math";
import type { WordResult } from "@/api/types";
import HintButton from "./HintButton";

interface MissingNumberProps {
  sessionSlug: string;
  onFinish: (score: number, maxScore: number, wordResults: WordResult[]) => void;
}

export default function MissingNumber({ sessionSlug, onFinish }: MissingNumberProps) {
  const engine = useGameEngine({
    totalRounds: 8,
    starsPerCorrect: 1,
    answerDelay: 1500,
  });

  const problems = useMemo(
    () => Array.from({ length: 8 }, () => generateMissingNumberProblem(sessionSlug)),
    [sessionSlug],
  );

  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);

  const problem: MissingNumberProblem = problems[engine.currentRound]!;

  const options = useMemo(() => {
    const distractors = generateDistractors(problem.missingValue, 3);
    return shuffle([problem.missingValue, ...distractors]);
  }, [problem]);

  if (engine.isFinished) {
    setTimeout(() => onFinish(engine.gameScore, engine.maxScore, engine.wordResults), 0);
    return null;
  }

  const handleOptionClick = (value: number) => {
    if (engine.isAnswering) return;
    setSelectedAnswer(value);
    const correct = value === problem.missingValue;

    const result: WordResult = {
      word: problem.originalProblem.equation,
      correct,
      category: problem.originalProblem.category,
    };

    engine.submitAnswer(correct, [result]);
    setTimeout(() => setSelectedAnswer(null), 1500);
  };

  const getOptionColor = (value: number) => {
    if (!engine.isAnswering || selectedAnswer === null) return {};
    if (value === problem.missingValue) {
      return { borderColor: "#22c55e", bgcolor: "#dcfce7" };
    }
    if (value === selectedAnswer && value !== problem.missingValue) {
      return { borderColor: "#ef4444", bgcolor: "#fee2e2" };
    }
    return {};
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", px: 2, py: 3, gap: 3 }}>
      {/* Progress bar */}
      <Box sx={{ width: "100%", maxWidth: 500 }}>
        <LinearProgress
          variant="determinate"
          value={engine.progressPercent}
          sx={{
            height: 8,
            borderRadius: 4,
            bgcolor: "rgba(0,0,0,0.08)",
            "& .MuiLinearProgress-bar": {
              borderRadius: 4,
              background: "linear-gradient(90deg, #6ee7b7, #10b981)",
            },
          }}
        />
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ display: "block", textAlign: "center", mt: 0.5 }}
        >
          {engine.currentRound + 1} / {engine.totalRounds}
        </Typography>
      </Box>

      {/* Equation card with blank */}
      <Box
        sx={{
          width: "100%",
          maxWidth: 500,
          bgcolor: "white",
          borderRadius: 4,
          p: { xs: 3, sm: 4 },
          boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 2,
          animation: "popIn 0.3s ease-out",
        }}
      >
        <Typography
          sx={{
            fontFamily: "'Fredoka', sans-serif",
            fontWeight: 600,
            fontSize: { xs: "1.5rem", sm: "2rem" },
            direction: "ltr",
            textAlign: "center",
          }}
        >
          {problem.displayEquation}
        </Typography>
        <HintButton hint={problem.hint} />
      </Box>

      {/* 4-button multiple choice */}
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 2,
          width: "100%",
          maxWidth: 400,
        }}
      >
        {options.map((value) => (
          <Button
            key={value}
            onClick={() => handleOptionClick(value)}
            disabled={engine.isAnswering}
            sx={{
              py: 2,
              borderRadius: 3,
              border: "2px solid rgba(0,0,0,0.12)",
              fontFamily: "'Fredoka', sans-serif",
              fontWeight: 600,
              fontSize: { xs: "1.2rem", sm: "1.4rem" },
              textTransform: "none",
              bgcolor: "white",
              color: "text.primary",
              direction: "ltr",
              minHeight: 56,
              "&:hover": {
                bgcolor: engine.isAnswering ? undefined : "#ecfdf5",
                borderColor: engine.isAnswering ? undefined : "#10b981",
              },
              "&.Mui-disabled": {
                color: "text.primary",
              },
              ...getOptionColor(value),
            }}
          >
            {value}
          </Button>
        ))}
      </Box>
    </Box>
  );
}
