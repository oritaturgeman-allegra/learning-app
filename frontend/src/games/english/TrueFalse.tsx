/**
 * Game 4: True or False — נכון או לא?
 *
 * Shows English sentence + Hebrew translation + speaker button.
 * Player answers Yes or No.
 * 1 star per correct answer, 8 rounds.
 */

import { useMemo, useState } from "react";
import { Box, Button, LinearProgress, Typography } from "@mui/material";
import VolumeUpIcon from "@mui/icons-material/VolumeUp";
import { speak } from "@/hooks/useAudio";
import { useGameEngine } from "@/hooks/useGameEngine";
import { shuffle, getWordsInSentence } from "@/data/english";
import type { TrueFalseSentence, VocabWord } from "@/data/english";
import type { WordResult } from "@/api/types";

interface TrueFalseProps {
  sentences: TrueFalseSentence[];
  vocabulary: VocabWord[];
  onFinish: (score: number, maxScore: number, wordResults: WordResult[]) => void;
}

export default function TrueFalse({ sentences, vocabulary, onFinish }: TrueFalseProps) {
  const gameSentences = useMemo(() => shuffle(sentences), [sentences]);

  const engine = useGameEngine({
    totalRounds: gameSentences.length,
    starsPerCorrect: 1,
    answerDelay: 1500,
  });

  const [selectedAnswer, setSelectedAnswer] = useState<boolean | null>(null);

  const currentSentence = gameSentences[engine.currentRound];

  // Trigger onFinish when game ends
  if (engine.isFinished) {
    setTimeout(() => onFinish(engine.gameScore, engine.maxScore, engine.wordResults), 0);
    return null;
  }

  if (!currentSentence) return null;

  const handleAnswer = (answer: boolean) => {
    if (engine.isAnswering) return;
    const correct = answer === currentSentence.answer;
    setSelectedAnswer(answer);

    // Build word results from vocabulary words in the sentence
    const coveredWords = getWordsInSentence(currentSentence, vocabulary);
    const results: WordResult[] = coveredWords.map((w) => ({
      word: w,
      correct,
      category: "true_false",
    }));

    engine.submitAnswer(correct, results);

    setTimeout(() => setSelectedAnswer(null), 1500);
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
              background: "linear-gradient(90deg, #f9a8d4, #ec4899)",
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

      {/* Sentence card */}
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
          gap: 1.5,
          animation: "popIn 0.3s ease-out",
        }}
      >
        <Typography
          sx={{
            fontFamily: "'Fredoka', sans-serif",
            fontWeight: 600,
            fontSize: { xs: "1.2rem", sm: "1.5rem" },
            direction: "ltr",
            textAlign: "center",
          }}
        >
          {currentSentence.english}
        </Typography>
        <Typography
          sx={{
            fontFamily: "'Rubik', sans-serif",
            fontSize: { xs: "1rem", sm: "1.2rem" },
            color: "text.secondary",
            textAlign: "center",
          }}
        >
          {currentSentence.hebrew}
        </Typography>
        <Button
          onClick={() => speak(currentSentence.english)}
          sx={{ minWidth: 0, fontSize: "1.3rem", p: 0.5, borderRadius: "50%" }}
        >
          <VolumeUpIcon />
        </Button>
      </Box>

      {/* True/False buttons */}
      <Box sx={{ display: "flex", gap: 2, width: "100%", maxWidth: 400 }}>
        {/* Yes button */}
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
            borderColor:
              engine.isAnswering && selectedAnswer === true && currentSentence.answer === true
                ? "#22c55e"
                : engine.isAnswering && selectedAnswer === true && currentSentence.answer !== true
                  ? "#ef4444"
                  : engine.isAnswering && selectedAnswer !== true && currentSentence.answer === true
                    ? "#22c55e"
                    : "rgba(0,0,0,0.12)",
            bgcolor:
              engine.isAnswering && selectedAnswer === true && currentSentence.answer === true
                ? "#dcfce7"
                : engine.isAnswering && selectedAnswer === true && currentSentence.answer !== true
                  ? "#fee2e2"
                  : engine.isAnswering && selectedAnswer !== true && currentSentence.answer === true
                    ? "#dcfce7"
                    : "white",
            color: "text.primary",
            "&:hover": {
              bgcolor: engine.isAnswering ? undefined : "#dcfce7",
              borderColor: engine.isAnswering ? undefined : "#22c55e",
            },
            "&.Mui-disabled": {
              color: "text.primary",
            },
          }}
        >
          כן ✅
        </Button>

        {/* No button */}
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
            borderColor:
              engine.isAnswering && selectedAnswer === false && currentSentence.answer === false
                ? "#22c55e"
                : engine.isAnswering && selectedAnswer === false && currentSentence.answer !== false
                  ? "#ef4444"
                  : engine.isAnswering && selectedAnswer !== false && currentSentence.answer === false
                    ? "#22c55e"
                    : "rgba(0,0,0,0.12)",
            bgcolor:
              engine.isAnswering && selectedAnswer === false && currentSentence.answer === false
                ? "#dcfce7"
                : engine.isAnswering && selectedAnswer === false && currentSentence.answer !== false
                  ? "#fee2e2"
                  : engine.isAnswering && selectedAnswer !== false && currentSentence.answer === false
                    ? "#dcfce7"
                    : "white",
            color: "text.primary",
            "&:hover": {
              bgcolor: engine.isAnswering ? undefined : "#fee2e2",
              borderColor: engine.isAnswering ? undefined : "#ef4444",
            },
            "&.Mui-disabled": {
              color: "text.primary",
            },
          }}
        >
          לא ❌
        </Button>
      </Box>
    </Box>
  );
}
