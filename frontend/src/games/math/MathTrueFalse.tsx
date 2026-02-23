/**
 * Game 3: Math True/False — נכון או לא?
 *
 * 10 rounds, 1 star per correct answer.
 * Shows a math equation (correct or wrong), player answers Yes or No.
 * On wrong answer, shows the correct equation.
 */

import { useMemo, useState } from "react";
import { Box, Button, LinearProgress, Typography } from "@mui/material";
import { useGameEngine } from "@/hooks/useGameEngine";
import { generateTFProblem } from "@/data/math";
import type { TFProblem } from "@/data/math";
import type { WordResult } from "@/api/types";
import HintButton from "./HintButton";

interface MathTrueFalseProps {
  sessionSlug: string;
  onFinish: (score: number, maxScore: number, wordResults: WordResult[]) => void;
}

export default function MathTrueFalse({ sessionSlug, onFinish }: MathTrueFalseProps) {
  const engine = useGameEngine({
    totalRounds: 10,
    starsPerCorrect: 1,
    answerDelay: 1500,
  });

  const problems = useMemo(
    () => Array.from({ length: 10 }, () => generateTFProblem(sessionSlug)),
    [sessionSlug],
  );

  const [selectedAnswer, setSelectedAnswer] = useState<boolean | null>(null);

  const problem: TFProblem = problems[engine.currentRound]!;

  if (engine.isFinished) {
    setTimeout(() => onFinish(engine.gameScore, engine.maxScore, engine.wordResults), 0);
    return null;
  }

  const handleAnswer = (answer: boolean) => {
    if (engine.isAnswering) return;
    const correct = answer === problem.isTrue;
    setSelectedAnswer(answer);

    const result: WordResult = {
      word: problem.display,
      correct,
      category: "true_false_math",
    };

    engine.submitAnswer(correct, [result]);
    setTimeout(() => setSelectedAnswer(null), 1500);
  };

  // Was the user's answer wrong?
  const answeredWrong =
    engine.isAnswering && selectedAnswer !== null && selectedAnswer !== problem.isTrue;

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
              background: "linear-gradient(90deg, #fda4af, #f43f5e)",
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

      {/* Equation card */}
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
          {problem.display}
        </Typography>
        <HintButton hint={problem.hint} />
      </Box>

      {/* Correct answer feedback on wrong */}
      {answeredWrong && (
        <Box
          sx={{
            width: "100%",
            maxWidth: 500,
            bgcolor: "#dcfce7",
            borderRadius: 3,
            p: 2,
            textAlign: "center",
            border: "1px solid #22c55e",
          }}
        >
          <Typography
            sx={{
              fontFamily: "'Fredoka', sans-serif",
              fontWeight: 600,
              fontSize: "1.1rem",
              color: "#166534",
              direction: "ltr",
            }}
          >
            {problem.correctDisplay}
          </Typography>
        </Box>
      )}

      {/* True/False buttons */}
      <Box sx={{ display: "flex", gap: 2, width: "100%", maxWidth: 400 }}>
        <Button
          onClick={() => handleAnswer(true)}
          disabled={engine.isAnswering}
          sx={{
            flex: 1,
            py: 2,
            borderRadius: 3,
            border: "2px solid",
            fontFamily: "'Fredoka', sans-serif",
            fontWeight: 600,
            fontSize: "1.2rem",
            textTransform: "none",
            minHeight: 56,
            borderColor:
              engine.isAnswering && selectedAnswer === true && problem.isTrue
                ? "#22c55e"
                : engine.isAnswering && selectedAnswer === true && !problem.isTrue
                  ? "#ef4444"
                  : engine.isAnswering && selectedAnswer !== true && problem.isTrue
                    ? "#22c55e"
                    : "rgba(0,0,0,0.12)",
            bgcolor:
              engine.isAnswering && selectedAnswer === true && problem.isTrue
                ? "#dcfce7"
                : engine.isAnswering && selectedAnswer === true && !problem.isTrue
                  ? "#fee2e2"
                  : engine.isAnswering && selectedAnswer !== true && problem.isTrue
                    ? "#dcfce7"
                    : "white",
            color: "text.primary",
            "&:hover": {
              bgcolor: engine.isAnswering ? undefined : "#dcfce7",
              borderColor: engine.isAnswering ? undefined : "#22c55e",
            },
            "&.Mui-disabled": { color: "text.primary" },
          }}
        >
          נכון ✅
        </Button>

        <Button
          onClick={() => handleAnswer(false)}
          disabled={engine.isAnswering}
          sx={{
            flex: 1,
            py: 2,
            borderRadius: 3,
            border: "2px solid",
            fontFamily: "'Fredoka', sans-serif",
            fontWeight: 600,
            fontSize: "1.2rem",
            textTransform: "none",
            minHeight: 56,
            borderColor:
              engine.isAnswering && selectedAnswer === false && !problem.isTrue
                ? "#22c55e"
                : engine.isAnswering && selectedAnswer === false && problem.isTrue
                  ? "#ef4444"
                  : engine.isAnswering && selectedAnswer !== false && !problem.isTrue
                    ? "#22c55e"
                    : "rgba(0,0,0,0.12)",
            bgcolor:
              engine.isAnswering && selectedAnswer === false && !problem.isTrue
                ? "#dcfce7"
                : engine.isAnswering && selectedAnswer === false && problem.isTrue
                  ? "#fee2e2"
                  : engine.isAnswering && selectedAnswer !== false && !problem.isTrue
                    ? "#dcfce7"
                    : "white",
            color: "text.primary",
            "&:hover": {
              bgcolor: engine.isAnswering ? undefined : "#fee2e2",
              borderColor: engine.isAnswering ? undefined : "#ef4444",
            },
            "&.Mui-disabled": { color: "text.primary" },
          }}
        >
          לא נכון ❌
        </Button>
      </Box>
    </Box>
  );
}
