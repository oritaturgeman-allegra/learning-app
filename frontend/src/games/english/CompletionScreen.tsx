/**
 * CompletionScreen — shown after finishing all rounds of a game.
 * Displays score summary with celebration and replay/back buttons.
 */

import { useEffect } from "react";
import { Box, Button, Typography } from "@mui/material";
import { playCelebration } from "@/hooks/useAudio";

interface CompletionScreenProps {
  score: number;
  maxScore: number;
  onReplay: () => void;
  onBackToMenu: () => void;
}

export default function CompletionScreen({
  score,
  maxScore,
  onReplay,
  onBackToMenu,
}: CompletionScreenProps) {
  useEffect(() => {
    playCelebration();
  }, []);

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "calc(100vh - 72px)",
        textAlign: "center",
        px: 3,
        gap: 3,
      }}
    >
      {/* Celebration emoji */}
      <Typography sx={{ fontSize: "4rem", animation: "bounceIn 0.6s ease-out" }}>
        🎉
      </Typography>

      {/* Title */}
      <Typography
        variant="h4"
        sx={{
          fontFamily: "'Fredoka', sans-serif",
          fontWeight: 700,
          animation: "bounceIn 0.6s ease-out 0.1s both",
        }}
      >
        כל הכבוד אריאל!
      </Typography>

      {/* Score */}
      <Typography
        variant="h5"
        sx={{
          fontFamily: "'Fredoka', sans-serif",
          fontWeight: 600,
          color: "text.secondary",
          animation: "bounceIn 0.6s ease-out 0.2s both",
        }}
      >
        {score} / {maxScore} כוכבים הרווחת ⭐
      </Typography>

      {/* Buttons */}
      <Box
        sx={{
          display: "flex",
          gap: 2,
          flexWrap: "wrap",
          justifyContent: "center",
          animation: "bounceIn 0.6s ease-out 0.3s both",
        }}
      >
        <Button
          variant="contained"
          onClick={onBackToMenu}
          sx={{
            fontFamily: "'Fredoka', sans-serif",
            fontWeight: 600,
            fontSize: "1.1rem",
            borderRadius: 9999,
            px: 3,
            py: 1.5,
            minHeight: 48,
          }}
        >
          חזרה לתפריט 🏠
        </Button>
        <Button
          variant="outlined"
          onClick={onReplay}
          sx={{
            fontFamily: "'Fredoka', sans-serif",
            fontWeight: 600,
            fontSize: "1.1rem",
            borderRadius: 9999,
            px: 3,
            py: 1.5,
            minHeight: 48,
          }}
        >
          שחקי שוב 🔄
        </Button>
      </Box>
    </Box>
  );
}
