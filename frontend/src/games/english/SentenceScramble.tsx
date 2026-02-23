/**
 * Game 2: Sentence Scramble — תרגמי את המשפט
 *
 * Shows Hebrew translation. Player assembles the English sentence
 * by clicking scrambled word chips into a drop zone.
 * 2 stars per correct answer, 6 rounds.
 */

import { useEffect, useMemo, useState } from "react";
import { Box, Button, Chip, LinearProgress, Typography } from "@mui/material";
import VolumeUpIcon from "@mui/icons-material/VolumeUp";
import { speak } from "@/hooks/useAudio";
import { useGameEngine } from "@/hooks/useGameEngine";
import { shuffle, getWordsInSentence } from "@/data/english";
import type { ScrambleSentence, VocabWord } from "@/data/english";
import type { WordResult } from "@/api/types";

interface SentenceScrambleProps {
  sentences: ScrambleSentence[];
  vocabulary: VocabWord[];
  onFinish: (score: number, maxScore: number, wordResults: WordResult[]) => void;
}

export default function SentenceScramble({ sentences, vocabulary, onFinish }: SentenceScrambleProps) {
  const gameSentences = useMemo(() => shuffle(sentences), [sentences]);

  const engine = useGameEngine({
    totalRounds: gameSentences.length,
    starsPerCorrect: 2,
    answerDelay: 2500,
  });

  const [placedWords, setPlacedWords] = useState<{ word: string; index: number }[]>([]);
  const [feedback, setFeedback] = useState<"correct" | "wrong" | null>(null);

  const currentSentence = gameSentences[engine.currentRound];

  // Scrambled word chips for current sentence
  const scrambledWords = useMemo(() => {
    if (!currentSentence) return [];
    const words = currentSentence.english.split(" ");
    return shuffle(words.map((w, i) => ({ word: w, originalIndex: i })));
  }, [currentSentence]);

  // Reset placed words when round changes
  useEffect(() => {
    setPlacedWords([]);
    setFeedback(null);
  }, [engine.currentRound]);

  // Trigger onFinish when game ends
  if (engine.isFinished) {
    setTimeout(() => onFinish(engine.gameScore, engine.maxScore, engine.wordResults), 0);
    return null;
  }

  if (!currentSentence) return null;

  const placedIndices = new Set(placedWords.map((p) => p.index));

  const handleAddWord = (word: string, index: number) => {
    if (engine.isAnswering) return;
    if (placedIndices.has(index)) return;
    setPlacedWords((prev) => [...prev, { word, index }]);
  };

  const handleRemoveWord = (position: number) => {
    if (engine.isAnswering) return;
    setPlacedWords((prev) => prev.filter((_, i) => i !== position));
  };

  const handleCheck = () => {
    if (engine.isAnswering || placedWords.length === 0) return;

    const userSentence = placedWords.map((p) => p.word).join(" ");
    const correct = userSentence.toLowerCase() === currentSentence.english.toLowerCase();

    setFeedback(correct ? "correct" : "wrong");

    // Build word results from vocabulary words in the sentence
    const coveredWords = getWordsInSentence(currentSentence, vocabulary);
    const results: WordResult[] = coveredWords.map((w) => ({
      word: w,
      correct,
      category: "sentence",
    }));

    engine.submitAnswer(correct, results);
    speak(currentSentence.english);
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
              background: "linear-gradient(90deg, #fdba74, #f97316)",
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
          gap: 1,
          animation: "popIn 0.3s ease-out",
        }}
      >
        <Typography
          sx={{
            fontFamily: "'Rubik', sans-serif",
            fontWeight: 600,
            fontSize: { xs: "1.2rem", sm: "1.4rem" },
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

      {/* Drop zone */}
      <Box
        sx={{
          width: "100%",
          maxWidth: 500,
          minHeight: 56,
          border: "2px dashed",
          borderColor: feedback === "correct" ? "#22c55e" : feedback === "wrong" ? "#ef4444" : "rgba(0,0,0,0.2)",
          borderRadius: 3,
          display: "flex",
          flexWrap: "wrap",
          gap: 0.75,
          p: 1.5,
          justifyContent: "center",
          alignItems: "center",
          direction: "ltr",
          bgcolor: feedback === "correct" ? "#dcfce7" : feedback === "wrong" ? "#fee2e2" : "rgba(255,255,255,0.6)",
        }}
      >
        {placedWords.length === 0 ? (
          <Typography color="text.disabled" sx={{ fontSize: "0.9rem" }}>
            ...לחצי על מילים כדי לבנות משפט
          </Typography>
        ) : (
          placedWords.map((item, i) => (
            <Chip
              key={`${item.index}-${i}`}
              label={item.word}
              onClick={() => handleRemoveWord(i)}
              disabled={engine.isAnswering}
              sx={{
                fontFamily: "'Fredoka', sans-serif",
                fontWeight: 500,
                fontSize: "0.95rem",
                cursor: engine.isAnswering ? "default" : "pointer",
              }}
            />
          ))
        )}
      </Box>

      {/* Word chips to pick from */}
      <Box
        sx={{
          display: "flex",
          flexWrap: "wrap",
          gap: 1,
          justifyContent: "center",
          width: "100%",
          maxWidth: 500,
          direction: "ltr",
        }}
      >
        {scrambledWords.map((item, i) => {
          const isPlaced = placedIndices.has(i);
          return (
            <Chip
              key={`${item.word}-${i}`}
              label={item.word}
              onClick={() => handleAddWord(item.word, i)}
              disabled={engine.isAnswering || isPlaced}
              sx={{
                fontFamily: "'Fredoka', sans-serif",
                fontWeight: 500,
                fontSize: "0.95rem",
                animation: `popIn 0.3s ease-out ${i * 0.06}s both`,
                opacity: isPlaced ? 0.3 : 1,
                cursor: isPlaced || engine.isAnswering ? "default" : "pointer",
              }}
            />
          );
        })}
      </Box>

      {/* Check button */}
      <Button
        variant="contained"
        onClick={handleCheck}
        disabled={engine.isAnswering || placedWords.length === 0}
        sx={{
          fontFamily: "'Fredoka', sans-serif",
          fontWeight: 600,
          fontSize: "1.05rem",
          borderRadius: 9999,
          px: 4,
          py: 1.2,
        }}
      >
        בדקי ✓
      </Button>

      {/* Feedback */}
      {feedback && (
        <Typography
          sx={{
            fontFamily: "'Fredoka', sans-serif",
            fontWeight: 600,
            fontSize: "1.1rem",
            color: feedback === "correct" ? "#16a34a" : "#dc2626",
            animation: "popIn 0.3s ease-out",
          }}
        >
          {feedback === "correct" ? "מצוין! ✅" : `❌ ${currentSentence.english}`}
        </Typography>
      )}
    </Box>
  );
}
