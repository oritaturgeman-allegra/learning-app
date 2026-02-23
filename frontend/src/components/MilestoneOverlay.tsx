/**
 * Milestone celebration overlay — shown every 5 stars.
 * Standard: 🎉 + "כל הכבוד אריאל!" (2.5s)
 * Parade (every 10 stars): 🏆 + floating emojis (3s)
 *
 * Ported from showMilestone() and showEmojiParade() in shared.js.
 */

import { useEffect, useState } from "react";
import { Backdrop, Box, Typography } from "@mui/material";

const PARADE_EMOJIS = ["🎊", "🎉", "🏆", "🎉", "🎊", "⭐", "🌟", "💫"];

interface Props {
  open: boolean;
  stars: number;
  isParade: boolean;
  onClose: () => void;
}

export default function MilestoneOverlay({ open, stars, isParade, onClose }: Props) {
  const [paradeEmojis, setParadeEmojis] = useState<Array<{ id: number; emoji: string; left: string; delay: string }>>([]);

  // Auto-close after 2.5s (standard) or 3s (parade)
  useEffect(() => {
    if (!open) return;
    const timer = setTimeout(onClose, isParade ? 3000 : 2500);
    return () => clearTimeout(timer);
  }, [open, isParade, onClose]);

  // Spawn parade emojis with staggered delays
  useEffect(() => {
    if (!open || !isParade) {
      setParadeEmojis([]);
      return;
    }
    const emojis = PARADE_EMOJIS.map((emoji, i) => ({
      id: i,
      emoji,
      left: `${10 + Math.random() * 80}%`,
      delay: `${i * 0.2 + Math.random() * 0.5}s`,
    }));
    setParadeEmojis(emojis);
  }, [open, isParade]);

  return (
    <Backdrop
      open={open}
      sx={{
        zIndex: 1500,
        bgcolor: "rgba(0,0,0,0.5)",
        flexDirection: "column",
      }}
    >
      {/* Main content */}
      <Box
        sx={{
          textAlign: "center",
          animation: "popIn 0.4s ease-out",
        }}
      >
        <Typography sx={{ fontSize: "4rem", mb: 1 }}>
          {isParade ? "🏆" : "🎉"}
        </Typography>
        <Typography
          variant="h4"
          sx={{
            color: "white",
            fontWeight: 700,
            mb: 1,
          }}
        >
          כל הכבוד אריאל!
        </Typography>
        <Typography
          variant="h6"
          sx={{ color: "rgba(255,255,255,0.9)" }}
        >
          {isParade ? `🌟 ${stars} כוכבים — מדהים!` : `⭐ ${stars} כוכבים!`}
        </Typography>
      </Box>

      {/* Parade emojis */}
      {isParade &&
        paradeEmojis.map((p) => (
          <Box
            key={p.id}
            sx={{
              position: "fixed",
              left: p.left,
              bottom: 0,
              fontSize: "3rem",
              animation: `emojiParade 2.5s ease-out ${p.delay} forwards`,
              pointerEvents: "none",
            }}
          >
            {p.emoji}
          </Box>
        ))}
    </Backdrop>
  );
}
