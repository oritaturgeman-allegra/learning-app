/**
 * Game menu — 4 game cards for a session.
 * Shows subject tabs, game cards with colors, and completion state.
 * English games navigate to play screen; math games show "coming soon".
 */

import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Box, Card, CardActionArea, Snackbar, Stack, Tab, Tabs, Typography } from "@mui/material";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import { GAMES_BY_SUBJECT } from "@/data/games";
import { getUnitData } from "@/data/english";
import { getPracticedWords } from "@/api/game";
import WordTracker from "@/games/english/WordTracker";

const SUBJECT_TABS = [
  { id: "english", label: "אנגלית", icon: "/static/input-letters-light.svg" },
  { id: "math", label: "חשבון", icon: "/static/input-numbers-light.svg" },
];

const SS_COMPLETED_KEY = "ariel_session_completed_games";

function getCompletedGames(sessionSlug: string): Set<number> {
  try {
    const raw = sessionStorage.getItem(`${SS_COMPLETED_KEY}_${sessionSlug}`);
    return new Set(raw ? (JSON.parse(raw) as number[]) : []);
  } catch {
    return new Set();
  }
}

export default function GameMenu() {
  const { subject, sessionSlug } = useParams<{ subject: string; sessionSlug: string }>();
  const navigate = useNavigate();
  const [snackOpen, setSnackOpen] = useState(false);
  const [completedGames, setCompletedGames] = useState<Set<number>>(new Set());
  const [practicedWords, setPracticedWords] = useState<Set<string>>(new Set());

  const currentSubject = subject || "english";
  const slug = sessionSlug || "jet2-unit2";
  const games = GAMES_BY_SUBJECT[currentSubject] || [];
  const isEnglish = currentSubject === "english";
  const unit = isEnglish ? getUnitData(slug) : null;

  // Load completed games and practiced words
  useEffect(() => {
    setCompletedGames(getCompletedGames(slug));
    if (isEnglish) {
      getPracticedWords(slug)
        .then((res) => {
          if (res.success) {
            setPracticedWords(new Set(res.data.practiced_words));
          }
        })
        .catch(() => {});
    }
  }, [slug, isEnglish]);

  const handleTabChange = (_: React.SyntheticEvent, newValue: string) => {
    navigate(`/learning/${newValue}`);
  };

  const handleGameClick = (gameId: number) => {
    if (isEnglish) {
      navigate(`play/${gameId}`);
    } else {
      // Math games not yet implemented
      setSnackOpen(true);
    }
  };

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        px: 3,
        py: { xs: 3, sm: 5 },
      }}
    >
      {/* Subject tabs */}
      <Tabs
        value={currentSubject}
        onChange={handleTabChange}
        sx={{
          mb: 3,
          "& .MuiTab-root": {
            fontFamily: "'Fredoka', sans-serif",
            fontWeight: 600,
            fontSize: "0.95rem",
            minHeight: 44,
            textTransform: "none",
            gap: 0.75,
          },
        }}
      >
        {SUBJECT_TABS.map((tab) => (
          <Tab
            key={tab.id}
            value={tab.id}
            label={tab.label}
            onClick={() => navigate(`/learning/${tab.id}`)}
            icon={
              <Box
                component="img"
                src={tab.icon}
                alt={tab.label}
                sx={{ width: 24, height: 24 }}
              />
            }
            iconPosition="start"
          />
        ))}
      </Tabs>

      {/* Title */}
      <Typography
        variant="h4"
        sx={{
          fontWeight: 700,
          mb: 3,
          animation: "bounceIn 0.6s ease-out",
          fontSize: { xs: "1.4rem", sm: "1.8rem" },
        }}
      >
        אריאל, בחרי משחק 🎮
      </Typography>

      {/* Session slug display */}
      {sessionSlug && (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mb: 2, opacity: 0.7 }}
        >
          {sessionSlug}
        </Typography>
      )}

      {/* Game cards */}
      <Stack spacing={2} sx={{ width: "100%", maxWidth: 500 }}>
        {games.map((game, i) => {
          const isCompleted = completedGames.has(game.id);
          return (
            <Card
              key={game.type}
              sx={{
                borderRadius: 4,
                bgcolor: game.color,
                boxShadow: "0 4px 16px rgba(0,0,0,0.1)",
                animation: `slideUp 0.5s ease-out ${0.1 + i * 0.12}s both`,
                "&:hover": {
                  transform: "translateY(-4px)",
                  boxShadow: "0 8px 24px rgba(0,0,0,0.15)",
                },
                transition: "transform 0.2s, box-shadow 0.2s",
                position: "relative",
              }}
            >
              <CardActionArea
                onClick={() => handleGameClick(game.id)}
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: 2,
                  p: { xs: 2, sm: 3 },
                  justifyContent: "flex-start",
                  minHeight: { xs: 80, sm: 100 },
                }}
              >
                {/* Game emoji */}
                <Typography
                  sx={{
                    fontSize: { xs: "2rem", sm: "2.5rem" },
                    minWidth: 48,
                    textAlign: "center",
                  }}
                >
                  {game.emoji}
                </Typography>

                {/* Game info */}
                <Box sx={{ flex: 1 }}>
                  <Typography
                    sx={{
                      fontFamily: "'Fredoka', sans-serif",
                      fontWeight: 600,
                      fontSize: { xs: "1.1rem", sm: "1.3rem" },
                      color: "white",
                    }}
                  >
                    {game.title}
                  </Typography>
                  <Typography
                    sx={{
                      fontSize: { xs: "0.85rem", sm: "0.95rem" },
                      color: "rgba(255,255,255,0.85)",
                    }}
                  >
                    {game.desc}
                  </Typography>
                </Box>

                {/* Completion checkmark */}
                {isCompleted && (
                  <CheckCircleIcon
                    sx={{
                      color: "rgba(255,255,255,0.9)",
                      fontSize: "1.5rem",
                    }}
                  />
                )}
              </CardActionArea>
            </Card>
          );
        })}
      </Stack>

      {/* Word tracker for English sessions */}
      {isEnglish && unit && (
        <WordTracker vocabulary={unit.vocabulary} practicedWords={practicedWords} />
      )}

      {/* "Coming soon" snackbar for math */}
      <Snackbar
        open={snackOpen}
        autoHideDuration={2000}
        onClose={() => setSnackOpen(false)}
        message="בקרוב! 🎮"
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      />
    </Box>
  );
}
