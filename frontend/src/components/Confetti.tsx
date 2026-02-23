/**
 * Confetti overlay — 30 colorful pieces falling from top.
 * Ported from spawnConfetti() in shared.js (lines 151-167).
 */

import { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import { Box } from "@mui/material";

const COLORS = ["#a855f7", "#f97316", "#eab308", "#ec4899", "#22c55e", "#3b82f6", "#ef4444"];
const PIECE_COUNT = 30;

interface ConfettiPiece {
  id: number;
  left: string;
  color: string;
  width: number;
  height: number;
  borderRadius: string;
  animationDelay: string;
  animationDuration: string;
}

function generatePieces(): ConfettiPiece[] {
  return Array.from({ length: PIECE_COUNT }, (_, i) => {
    const size = 6 + Math.random() * 8;
    return {
      id: i,
      left: `${Math.random() * 100}%`,
      color: COLORS[Math.floor(Math.random() * COLORS.length)]!,
      width: size,
      height: size,
      borderRadius: Math.random() > 0.5 ? "50%" : "2px",
      animationDelay: `${Math.random() * 0.8}s`,
      animationDuration: `${1.5 + Math.random() * 1.5}s`,
    };
  });
}

interface Props {
  active: boolean;
}

export default function Confetti({ active }: Props) {
  const [visible, setVisible] = useState(false);
  const pieces = useMemo(() => (active ? generatePieces() : []), [active]);

  useEffect(() => {
    if (active) {
      setVisible(true);
      const timer = setTimeout(() => setVisible(false), 3000);
      return () => clearTimeout(timer);
    }
    setVisible(false);
  }, [active]);

  if (!visible || pieces.length === 0) return null;

  return createPortal(
    <Box
      sx={{
        position: "fixed",
        inset: 0,
        pointerEvents: "none",
        zIndex: 9999,
        overflow: "hidden",
      }}
    >
      {pieces.map((p) => (
        <Box
          key={p.id}
          sx={{
            position: "absolute",
            top: 0,
            left: p.left,
            width: p.width,
            height: p.height,
            bgcolor: p.color,
            borderRadius: p.borderRadius,
            animation: `confettiFall ${p.animationDuration} linear ${p.animationDelay} forwards`,
          }}
        />
      ))}
    </Box>,
    document.body,
  );
}
