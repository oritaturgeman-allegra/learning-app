/**
 * Game 1: Word Match — מה המילה?
 *
 * Shows emoji + Hebrew word + speaker button.
 * Player picks the correct English translation from 4 options.
 * 1 star per correct answer.
 */

import { useMemo, useState } from "react";
import { Box, Button, LinearProgress, Typography } from "@mui/material";
import VolumeUpIcon from "@mui/icons-material/VolumeUp";
import { speak } from "@/hooks/useAudio";
import { useGameEngine } from "@/hooks/useGameEngine";
import { shuffle, pickRandom } from "@/data/english";
import type { VocabWord } from "@/data/english";
import type { WordResult } from "@/api/types";

interface WordMatchProps {
  words: VocabWord[];
  vocabulary: VocabWord[];
  onFinish: (score: number, maxScore: number, wordResults: WordResult[]) => void;
}

export default function WordMatch({ words, vocabulary, onFinish }: WordMatchProps) {
  const gameWords = useMemo(() => shuffle(words), [words]);

  const engine = useGameEngine({
    totalRounds: gameWords.length,
    starsPerCorrect: 1,
    answerDelay: 1500,
  });

  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);

  // Generate options for current round
  const currentWord = gameWords[engine.currentRound];
  const options = useMemo(() => {
    if (!currentWord) return [];
    const distractors = pickRandom(vocabulary, 3, currentWord);
    return shuffle([currentWord, ...distractors]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentWord, vocabulary]);

  // Trigger onFinish when game ends
  if (engine.isFinished) {
    // Use setTimeout to avoid calling onFinish during render
    setTimeout(() => onFinish(engine.gameScore, engine.maxScore, engine.wordResults), 0);
    return null;
  }

  if (!currentWord) return null;

  const handleAnswer = (option: VocabWord) => {
    if (engine.isAnswering) return;
    const correct = option.english === currentWord.english;
    setSelectedAnswer(option.english);

    const results: WordResult[] = [
      { word: currentWord.english, correct, category: currentWord.category },
    ];

    engine.submitAnswer(correct, results);
    speak(currentWord.english);

    // Reset selected after delay
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
              background: "linear-gradient(90deg, #c4b5fd, #a78bfa)",
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

      {/* Question area */}
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 1.5,
          animation: "popIn 0.3s ease-out",
        }}
      >
        <Typography sx={{ fontSize: "3.5rem" }}>{currentWord.emoji}</Typography>
        <Typography
          sx={{
            fontFamily: "'Rubik', sans-serif",
            fontWeight: 600,
            fontSize: { xs: "1.3rem", sm: "1.6rem" },
          }}
        >
          {currentWord.hebrew}
        </Typography>
        <Button
          onClick={() => speak(currentWord.english)}
          sx={{
            minWidth: 0,
            fontSize: "1.5rem",
            p: 1,
            borderRadius: "50%",
          }}
        >
          <VolumeUpIcon />
        </Button>
      </Box>

      {/* Answer options */}
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: { xs: "1fr 1fr", sm: "1fr 1fr" },
          gap: 1.5,
          width: "100%",
          maxWidth: 500,
        }}
      >
        {options.map((opt, i) => {
          const isSelected = selectedAnswer === opt.english;
          const isCorrectAnswer = opt.english === currentWord.english;
          let bgcolor = "white";
          let borderColor = "rgba(0,0,0,0.12)";

          if (engine.isAnswering && isSelected && isCorrectAnswer) {
            bgcolor = "#dcfce7";
            borderColor = "#22c55e";
          } else if (engine.isAnswering && isSelected && !isCorrectAnswer) {
            bgcolor = "#fee2e2";
            borderColor = "#ef4444";
          } else if (engine.isAnswering && !isSelected && isCorrectAnswer) {
            bgcolor = "#dcfce7";
            borderColor = "#22c55e";
          }

          return (
            <Button
              key={opt.english}
              onClick={() => handleAnswer(opt)}
              disabled={engine.isAnswering}
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 0.5,
                py: 2,
                px: 1.5,
                borderRadius: 3,
                border: `2px solid ${borderColor}`,
                bgcolor,
                color: "text.primary",
                textTransform: "none",
                animation: `popIn 0.3s ease-out ${i * 0.08}s both`,
                "&:hover": {
                  bgcolor: engine.isAnswering ? bgcolor : "#f5f3ff",
                  borderColor: engine.isAnswering ? borderColor : "#a78bfa",
                },
                "&.Mui-disabled": {
                  color: "text.primary",
                  bgcolor,
                  borderColor,
                },
              }}
            >
              <Typography sx={{ fontSize: "1.5rem" }}>{opt.emoji}</Typography>
              <Typography
                sx={{
                  fontFamily: "'Fredoka', sans-serif",
                  fontWeight: 500,
                  fontSize: "0.95rem",
                  direction: "ltr",
                }}
              >
                {opt.english}
              </Typography>
            </Button>
          );
        })}
      </Box>
    </Box>
  );
}
