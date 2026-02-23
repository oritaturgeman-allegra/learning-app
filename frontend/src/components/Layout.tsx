/**
 * Layout shell with sticky header for all screens except Welcome.
 * Uses React Router Outlet for nested route rendering.
 */

import { useState } from "react";
import { Outlet, Link, useLocation } from "react-router-dom";
import { Box, Button, Typography } from "@mui/material";
import StarCounter from "@/components/StarCounter";
import RewardCollection from "@/components/RewardCollection";
import { useApp } from "@/context/AppContext";

export default function Layout() {
  const [galleryOpen, setGalleryOpen] = useState(false);
  const { earnedRewards, rewardTiers } = useApp();
  const location = useLocation();

  // Hide home button on subject picker (already at top level)
  const isSubjectPicker = location.pathname === "/learning";
  const trophyFraction = `${earnedRewards.length}/${rewardTiers.length}`;

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "background.default" }}>
      {/* Sticky header */}
      <Box
        sx={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          zIndex: 20,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          px: { xs: 2, sm: 3 },
          py: 1.5,
          background: "linear-gradient(135deg, rgba(245,240,255,0.95), rgba(252,231,243,0.95))",
          backdropFilter: "blur(8px)",
        }}
      >
        {/* Right side (RTL: home button) */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          {!isSubjectPicker && (
            <Button
              component={Link}
              to="/learning"
              variant="outlined"
              size="small"
              sx={{
                minWidth: 0,
                height: 38,
                px: 1.5,
                borderRadius: 9999,
                borderColor: "rgba(0,0,0,0.12)",
                color: "text.secondary",
                fontSize: "1.2rem",
                "&:hover": {
                  borderColor: "primary.main",
                  color: "primary.main",
                },
              }}
            >
              🏠
            </Button>
          )}
        </Box>

        {/* Left side (RTL: star counter + trophy) */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <StarCounter />

          <Button
            onClick={() => setGalleryOpen(true)}
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 0.75,
              bgcolor: "#fef3c7",
              border: "2px solid #fde68a",
              borderRadius: 9999,
              px: 1.5,
              height: 38,
              minWidth: 0,
              color: "#f59e0b",
              "&:hover": {
                bgcolor: "#fde68a",
              },
            }}
          >
            <Typography component="span" sx={{ fontSize: "1.1rem", lineHeight: 1 }}>
              🏆
            </Typography>
            <Typography
              component="span"
              sx={{
                fontFamily: "'Fredoka', sans-serif",
                fontWeight: 600,
                fontSize: "0.85rem",
              }}
            >
              {trophyFraction}
            </Typography>
          </Button>
        </Box>
      </Box>

      {/* Page content — offset below fixed header */}
      <Box sx={{ pt: "72px" }}>
        <Outlet />
      </Box>

      {/* Trophy gallery dialog */}
      <RewardCollection open={galleryOpen} onClose={() => setGalleryOpen(false)} />
    </Box>
  );
}
