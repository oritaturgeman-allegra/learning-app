/**
 * Reward tier unlock popup — shows when a new reward is earned.
 * Auto-closes after 5 seconds. Uses rewardReveal animation.
 *
 * Ported from showRewardPopup() in shared.js (lines 272-294).
 */

import { useEffect } from "react";
import { Backdrop, Box, Button, Typography } from "@mui/material";
import type { RewardTier } from "@/api/types";

interface Props {
  tier: RewardTier | null;
  open: boolean;
  onClose: () => void;
}

export default function RewardPopup({ tier, open, onClose }: Props) {
  // Auto-close after 5 seconds
  useEffect(() => {
    if (!open) return;
    const timer = setTimeout(onClose, 5000);
    return () => clearTimeout(timer);
  }, [open, onClose]);

  if (!tier) return null;

  return (
    <Backdrop
      open={open}
      onClick={onClose}
      sx={{
        zIndex: 1600,
        bgcolor: "rgba(0,0,0,0.6)",
      }}
    >
      <Box
        onClick={(e) => e.stopPropagation()}
        sx={{
          bgcolor: "white",
          borderRadius: 6,
          p: 4,
          textAlign: "center",
          maxWidth: 320,
          width: "90%",
          animation: "rewardReveal 0.8s ease-out both",
          boxShadow: "0 8px 32px rgba(0,0,0,0.2)",
        }}
      >
        {/* Emoji */}
        <Typography sx={{ fontSize: "4rem", mb: 1 }}>
          {tier.emoji}
        </Typography>

        {/* English name */}
        <Typography
          variant="h5"
          sx={{
            fontFamily: "'Fredoka', sans-serif",
            fontWeight: 700,
            color: "#a855f7",
            mb: 0.5,
          }}
        >
          {tier.name_en}
        </Typography>

        {/* Hebrew name */}
        <Typography
          variant="h6"
          sx={{
            fontWeight: 600,
            mb: 1,
          }}
        >
          {tier.name_he}
        </Typography>

        {/* Description */}
        <Typography
          variant="body1"
          color="text.secondary"
          sx={{ mb: 1.5 }}
        >
          {tier.description_he}
        </Typography>

        {/* Star count */}
        <Typography
          sx={{
            fontFamily: "'Fredoka', sans-serif",
            fontWeight: 600,
            color: "#f59e0b",
            fontSize: "1.1rem",
            mb: 2,
          }}
        >
          ⭐ {tier.stars}
        </Typography>

        {/* Collect button */}
        <Button
          variant="contained"
          onClick={onClose}
          sx={{
            bgcolor: "#a855f7",
            fontWeight: 600,
            px: 4,
            "&:hover": { bgcolor: "#9333ea" },
          }}
        >
          אספתי!
        </Button>
      </Box>
    </Backdrop>
  );
}
