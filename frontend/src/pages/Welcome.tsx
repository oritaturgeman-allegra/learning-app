/**
 * Welcome / landing page — full-screen gradient with CTA button.
 * No header, no Layout wrapper. Standalone full-viewport screen.
 */

import { Link } from "react-router-dom";
import { Box, Button, Typography } from "@mui/material";

export default function Welcome() {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #a855f7, #ec4899, #f97316)",
        backgroundSize: "400% 400%",
        animation: "gradientCycle 6s ease infinite",
        textAlign: "center",
        p: 3,
      }}
    >
      {/* Title */}
      <Typography
        variant="h2"
        sx={{
          color: "white",
          fontWeight: 700,
          mb: 1,
          animation: "bounceIn 0.8s ease-out",
          fontSize: { xs: "2.5rem", sm: "3.5rem" },
        }}
      >
        שלום אריאל! 👋
      </Typography>

      {/* Subtitle */}
      <Typography
        variant="h6"
        sx={{
          color: "rgba(255,255,255,0.9)",
          mb: 4,
          animation: "bounceIn 1s ease-out 0.2s both",
          fontSize: { xs: "1.1rem", sm: "1.4rem" },
        }}
      >
        בואי ללמוד בכיף 🎉
      </Typography>

      {/* CTA button */}
      <Button
        variant="contained"
        size="large"
        component={Link}
        to="/learning"
        sx={{
          bgcolor: "white",
          color: "#a855f7",
          fontWeight: 700,
          fontSize: { xs: "1.2rem", sm: "1.4rem" },
          px: { xs: 4, sm: 5 },
          py: 1.5,
          animation: "bounceIn 1.2s ease-out 0.4s both",
          "&:hover": { bgcolor: "rgba(255,255,255,0.9)" },
        }}
      >
        מתחילים ▶️
      </Button>
    </Box>
  );
}
