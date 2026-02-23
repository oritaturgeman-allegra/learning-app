/**
 * Game 1: Quick Solve — פתרי מהר!
 *
 * 10 rounds, 1 star per correct answer.
 * Multiple-choice (4 options) for standard problems.
 * Dual input (quotient + remainder) for divide_remainder problems.
 */

import { useMemo, useState } from "react";
import { Box, Button, LinearProgress, TextField, Typography } from "@mui/material";
import { useGameEngine } from "@/hooks/useGameEngine";
import { generateProblem, generateDistractors } from "@/data/math";
import { shuffle } from "@/data/english";
import type { MathProblem } from "@/data/math";
import type { WordResult } from "@/api/types";
import HintButton from "./HintButton";

interface QuickSolveProps {
  sessionSlug: string;
  onFinish: (score: number, maxScore: number, wordResults: WordResult[]) => void;
}

export default function QuickSolve({ sessionSlug, onFinish }: QuickSolveProps) {
  const engine = useGameEngine({
    totalRounds: 10,
    starsPerCorrect: 1,
    answerDelay: 1500,
  });

  // Generate all problems upfront so they don't change on re-render
  const problems = useMemo(
    () => Array.from({ length: 10 }, () => generateProblem(sessionSlug)),
    [sessionSlug],
  );

  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [quotientInput, setQuotientInput] = useState("");
  const [remainderInput, setRemainderInput] = useState("");
  const [remainderSubmitted, setRemainderSubmitted] = useState(false);
  const [remainderCorrect, setRemainderCorrect] = useState(false);

  const problem: MathProblem = problems[engine.currentRound]!;
  const isRemainder = problem.remainder !== undefined;

  // Generate options for multiple-choice
  const options = useMemo(() => {
    if (isRemainder) return [];
    const distractors = generateDistractors(problem.answer, 3);
    return shuffle([problem.answer, ...distractors]);
  }, [problem, isRemainder]);

  // Trigger onFinish when game ends
  if (engine.isFinished) {
    setTimeout(() => onFinish(engine.gameScore, engine.maxScore, engine.wordResults), 0);
    return null;
  }

  const handleOptionClick = (value: number) => {
    if (engine.isAnswering) return;
    setSelectedAnswer(value);
    const correct = value === problem.answer;

    const result: WordResult = {
      word: problem.equation,
      correct,
      category: problem.category,
    };

    engine.submitAnswer(correct, [result]);
    setTimeout(() => setSelectedAnswer(null), 1500);
  };

  const handleRemainderSubmit = () => {
    if (engine.isAnswering || remainderSubmitted) return;
    const q = parseInt(quotientInput);
    const r = parseInt(remainderInput);
    const correct = q === problem.answer && r === problem.remainder;

    setRemainderSubmitted(true);
    setRemainderCorrect(correct);

    const result: WordResult = {
      word: problem.equation,
      correct,
      category: problem.category,
    };

    engine.submitAnswer(correct, [result]);

    setTimeout(() => {
      setQuotientInput("");
      setRemainderInput("");
      setRemainderSubmitted(false);
      setRemainderCorrect(false);
    }, 1500);
  };

  const getOptionColor = (value: number) => {
    if (!engine.isAnswering || selectedAnswer === null) return {};
    if (value === problem.answer) {
      return { borderColor: "#22c55e", bgcolor: "#dcfce7" };
    }
    if (value === selectedAnswer && value !== problem.answer) {
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
              background: "linear-gradient(90deg, #93c5fd, #3b82f6)",
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

      {/* Problem card */}
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

      {/* Answer area */}
      {isRemainder ? (
        /* Remainder input: quotient + remainder fields */
        <Box
          sx={{
            width: "100%",
            maxWidth: 400,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 2,
          }}
        >
          <Box sx={{ display: "flex", gap: 2, alignItems: "center", width: "100%" }}>
            <TextField
              value={quotientInput}
              onChange={(e) => setQuotientInput(e.target.value.replace(/\D/g, ""))}
              label="מנה"
              type="tel"
              disabled={engine.isAnswering}
              autoFocus
              sx={{
                flex: 1,
                "& .MuiOutlinedInput-root": {
                  borderRadius: 3,
                  fontFamily: "'Fredoka', sans-serif",
                  fontSize: "1.3rem",
                  ...(remainderSubmitted
                    ? {
                        borderColor: remainderCorrect ? "#22c55e" : "#ef4444",
                        "& fieldset": {
                          borderColor: remainderCorrect ? "#22c55e" : "#ef4444",
                          borderWidth: 2,
                        },
                      }
                    : {}),
                },
              }}
            />
            <Typography
              sx={{
                fontFamily: "'Fredoka', sans-serif",
                fontWeight: 600,
                fontSize: "1.2rem",
              }}
            >
              שארית
            </Typography>
            <TextField
              value={remainderInput}
              onChange={(e) => setRemainderInput(e.target.value.replace(/\D/g, ""))}
              label="שארית"
              type="tel"
              disabled={engine.isAnswering}
              sx={{
                width: 100,
                "& .MuiOutlinedInput-root": {
                  borderRadius: 3,
                  fontFamily: "'Fredoka', sans-serif",
                  fontSize: "1.3rem",
                  ...(remainderSubmitted
                    ? {
                        "& fieldset": {
                          borderColor: remainderCorrect ? "#22c55e" : "#ef4444",
                          borderWidth: 2,
                        },
                      }
                    : {}),
                },
              }}
            />
          </Box>

          {/* Correct answer feedback */}
          {remainderSubmitted && !remainderCorrect && (
            <Typography
              sx={{
                fontFamily: "'Fredoka', sans-serif",
                fontWeight: 600,
                fontSize: "1.1rem",
                color: "#22c55e",
              }}
            >
              {problem.answer} שארית {problem.remainder}
            </Typography>
          )}

          <Button
            variant="contained"
            onClick={handleRemainderSubmit}
            disabled={engine.isAnswering || !quotientInput || !remainderInput}
            sx={{
              fontFamily: "'Fredoka', sans-serif",
              fontWeight: 600,
              fontSize: "1.1rem",
              borderRadius: 9999,
              px: 4,
              py: 1.5,
              minHeight: 48,
            }}
          >
            בדקי!
          </Button>
        </Box>
      ) : (
        /* Multiple-choice: 4 option buttons */
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
                  bgcolor: engine.isAnswering ? undefined : "#eff6ff",
                  borderColor: engine.isAnswering ? undefined : "#3b82f6",
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
      )}
    </Box>
  );
}
