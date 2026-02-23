/**
 * Gold pill showing total star count.
 * Matches legacy .star-counter styling.
 */

import { Box, Typography } from "@mui/material";
import { useApp } from "@/context/AppContext";

export default function StarCounter() {
  const { totalStars } = useApp();

  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        gap: 0.75,
        bgcolor: "#fef3c7",
        border: "2px solid #fde68a",
        borderRadius: 9999,
        px: 1.5,
        py: 0.5,
        height: 38,
      }}
    >
      <Typography component="span" sx={{ fontSize: "1.2rem", lineHeight: 1 }}>
        ⭐
      </Typography>
      <Typography
        component="span"
        sx={{
          fontFamily: "'Fredoka', sans-serif",
          fontWeight: 600,
          fontSize: "1rem",
          color: "#f59e0b",
        }}
      >
        {totalStars}
      </Typography>
    </Box>
  );
}
