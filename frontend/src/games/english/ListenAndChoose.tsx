/**
 * Game 3: Listen & Choose — האזיני ובחרי
 *
 * Auto-speaks a word, player picks the correct one from 4 options
 * showing emoji + English + Hebrew.
 * 1 star per correct answer.
 */

import { useEffect, useMemo, useState } from "react";
import { Box, Button, LinearProgress, Typography } from "@mui/material";
import VolumeUpIcon from "@mui/icons-material/VolumeUp";
import { speak } from "@/hooks/useAudio";
import { useGameEngine } from "@/hooks/useGameEngine";
import { shuffle, pickRandom } from "@/data/english";
import type { VocabWord } from "@/data/english";
import type { WordResult } from "@/api/types";

interface ListenAndChooseProps {
  words: VocabWord[];
  vocabulary: VocabWord[];
  onFinish: (score: number, maxScore: number, wordResults: WordResult[]) => void;
}

export default function ListenAndChoose({ words, vocabulary, onFinish }: ListenAndChooseProps) {
  const gameWords = useMemo(() => shuffle(words), [words]);

  const engine = useGameEngine({
    totalRounds: gameWords.length,
    starsPerCorrect: 1,
    answerDelay: 1500,
  });

  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);

  const currentWord = gameWords[engine.currentRound];

  const options = useMemo(() => {
    if (!currentWord) return [];
    const distractors = pickRandom(vocabulary, 3, currentWord);
    return shuffle([currentWord, ...distractors]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentWord, vocabulary]);

  // Auto-speak word 500ms after round starts
  useEffect(() => {
    if (!currentWord || engine.isFinished) return;
    const timer = setTimeout(() => speak(currentWord.english), 500);
    return () => clearTimeout(timer);
  }, [currentWord, engine.currentRound, engine.isFinished]);

  // Trigger onFinish when game ends
  if (engine.isFinished) {
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
              background: "linear-gradient(90deg, #7dd3fc, #38bdf8)",
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
        <Typography
          sx={{
            fontFamily: "'Rubik', sans-serif",
            fontWeight: 600,
            fontSize: { xs: "1.2rem", sm: "1.4rem" },
          }}
        >
          מה המילה ששמעת?
        </Typography>
        <Button
          onClick={() => speak(currentWord.english)}
          variant="outlined"
          sx={{
            minWidth: 0,
            width: 64,
            height: 64,
            borderRadius: "50%",
            fontSize: "1.8rem",
          }}
        >
          <VolumeUpIcon sx={{ fontSize: "2rem" }} />
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
                  bgcolor: engine.isAnswering ? bgcolor : "#eff6ff",
                  borderColor: engine.isAnswering ? borderColor : "#38bdf8",
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
              <Typography
                sx={{
                  fontFamily: "'Rubik', sans-serif",
                  fontSize: "0.8rem",
                  color: "text.secondary",
                }}
              >
                {opt.hebrew}
              </Typography>
            </Button>
          );
        })}
      </Box>
    </Box>
  );
}
