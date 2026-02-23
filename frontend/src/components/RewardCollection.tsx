/**
 * Trophy gallery dialog showing earned and locked reward cards.
 * Matches legacy openCollection() behavior from shared.js.
 */

import {
  Box,
  Dialog,
  DialogContent,
  DialogTitle,
  Grid,
  IconButton,
  LinearProgress,
  Typography,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { useApp } from "@/context/AppContext";

interface Props {
  open: boolean;
  onClose: () => void;
}

export default function RewardCollection({ open, onClose }: Props) {
  const { rewardTiers, earnedRewards, nextReward, totalStars } = useApp();

  // Progress to next reward (0-100)
  const progressPercent = nextReward
    ? Math.min(100, Math.round((totalStars / nextReward.stars) * 100))
    : 100;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: { borderRadius: 4, p: 1 },
      }}
    >
      <DialogTitle
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          fontFamily: "'Fredoka', sans-serif",
          fontWeight: 600,
          pb: 1,
        }}
      >
        <Typography
          variant="h6"
          component="span"
          sx={{ fontFamily: "'Fredoka', sans-serif", fontWeight: 600 }}
        >
          🏆 האוסף שלי
        </Typography>
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent>
        {/* Progress to next reward */}
        {nextReward && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
              {nextReward.emoji} {nextReward.stars} ⭐ עד ל{nextReward.name_he}
            </Typography>
            <LinearProgress
              variant="determinate"
              value={progressPercent}
              sx={{
                height: 10,
                borderRadius: 5,
                bgcolor: "#f3e8ff",
                "& .MuiLinearProgress-bar": {
                  bgcolor: "#a855f7",
                  borderRadius: 5,
                },
              }}
            />
          </Box>
        )}

        {/* Reward cards grid */}
        <Grid container spacing={2}>
          {rewardTiers.map((tier) => {
            const earned = earnedRewards.includes(tier.id);
            return (
              <Grid size={{ xs: 6, sm: 4 }} key={tier.id}>
                <Box
                  sx={{
                    p: 2,
                    borderRadius: 3,
                    textAlign: "center",
                    border: earned ? "2px solid #f59e0b" : "2px dashed #d1d5db",
                    bgcolor: earned ? "#fffbeb" : "#f9fafb",
                    opacity: earned ? 1 : 0.5,
                    filter: earned ? "none" : "grayscale(1)",
                    transition: "all 0.3s ease",
                  }}
                >
                  <Typography sx={{ fontSize: "2rem", mb: 0.5 }}>
                    {tier.emoji}
                  </Typography>
                  <Typography
                    variant="body2"
                    sx={{
                      fontFamily: "'Fredoka', sans-serif",
                      fontWeight: 600,
                      mb: 0.25,
                    }}
                  >
                    {tier.name_he}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    ⭐ {tier.stars}
                  </Typography>
                  {earned && (
                    <Typography
                      variant="caption"
                      display="block"
                      sx={{ color: "#f59e0b", mt: 0.5 }}
                    >
                      {tier.description_he}
                    </Typography>
                  )}
                </Box>
              </Grid>
            );
          })}
        </Grid>
      </DialogContent>
    </Dialog>
  );
}
