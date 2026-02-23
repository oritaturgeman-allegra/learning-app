/**
 * Game menu — 4 game cards for a session.
 * Shows subject tabs, game cards with colors, and completion state.
 */

import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  Box, Button, Card, CardActionArea, Dialog, DialogActions, DialogContent,
  DialogTitle, IconButton, Stack, Tab, Tabs, Typography,
} from "@mui/material";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import CachedIcon from "@mui/icons-material/Cached";
import { GAMES_BY_SUBJECT } from "@/data/games";
import { getUnitData } from "@/data/english";
import { getPracticedWords, resetPracticedWords } from "@/api/game";
import { useApp } from "@/context/AppContext";
import WordTracker from "@/games/english/WordTracker";

const SUBJECT_TABS = [
  { id: "english", label: "אנגלית", icon: "/input-letters-light.svg" },
  { id: "math", label: "חשבון", icon: "/input-numbers-light.svg" },
];

const SS_PLAN_KEY = "ariel_session_plan";
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
  const [completedGames, setCompletedGames] = useState<Set<number>>(new Set());
  const [practicedWords, setPracticedWords] = useState<Set<string>>(new Set());
  const [resetOpen, setResetOpen] = useState(false);
  const [spinning, setSpinning] = useState(false);
  const resetBtnRef = useRef<HTMLButtonElement>(null);

  const { sessionsBySubject, clearSessionCompletion } = useApp();
  const currentSubject = subject || "english";
  const slug = sessionSlug || "jet2-unit2";
  const games = GAMES_BY_SUBJECT[currentSubject] || [];
  const isEnglish = currentSubject === "english";
  const unit = isEnglish ? getUnitData(slug) : null;
  const allSessions = sessionsBySubject[currentSubject] || [];
  const currentSession = allSessions.find((s) => s.slug === slug);

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
    navigate(`play/${gameId}`);
  };

  const handleReset = async () => {
    setResetOpen(false);
    setSpinning(true);
    try {
      await resetPracticedWords();
    } catch {
      // Reset still works client-side even if API fails
    }
    // Clear cached session plan → next game entry generates fresh words
    sessionStorage.removeItem(`${SS_PLAN_KEY}_${slug}`);
    // Clear completed games → cards become replayable
    sessionStorage.removeItem(`${SS_COMPLETED_KEY}_${slug}`);
    setCompletedGames(new Set());
    setPracticedWords(new Set());
    clearSessionCompletion(slug);
    setTimeout(() => setSpinning(false), 600);
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
      {/* Back button header */}
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 1,
          width: "100%",
          maxWidth: 500,
          mb: 2,
        }}
      >
        <IconButton onClick={() => navigate(-1)} size="small">
          <ArrowForwardIcon />
        </IconButton>
        <Typography
          sx={{
            fontFamily: "'Fredoka', sans-serif",
            fontWeight: 600,
            fontSize: { xs: "1.1rem", sm: "1.3rem" },
            flex: 1,
            textAlign: "center",
          }}
        >
          {currentSession
            ? isEnglish ? currentSession.name : currentSession.name_he
            : ""}
        </Typography>
        <Box sx={{ width: 34 }} />
      </Box>

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

      {/* Title + reset button */}
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 3 }}>
        <Typography
          variant="h4"
          sx={{
            fontWeight: 700,
            animation: "bounceIn 0.6s ease-out",
            fontSize: { xs: "1.4rem", sm: "1.8rem" },
          }}
        >
          אריאל, בחרי משחק 🎮
        </Typography>
        {isEnglish && (
          <IconButton
            ref={resetBtnRef}
            onClick={() => setResetOpen(true)}
            size="small"
            title="סבב חדש"
            sx={{
              color: "#a78bfa",
              transition: "transform 0.6s",
              ...(spinning && { animation: "spin 0.6s linear" }),
            }}
          >
            <CachedIcon />
          </IconButton>
        )}
      </Box>

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

      {/* Reset confirmation dialog */}
      <Dialog
        open={resetOpen}
        onClose={() => setResetOpen(false)}
        slotProps={{ paper: { sx: { borderRadius: 4, p: 1, textAlign: "center" } } }}
      >
        <DialogTitle sx={{ fontFamily: "'Fredoka', sans-serif", fontWeight: 700, fontSize: "1.3rem" }}>
          להתחיל סבב חדש?
        </DialogTitle>
        <DialogContent>
          <Typography sx={{ fontSize: "1rem", color: "text.secondary" }}>
            ⭐ הכוכבים נשארים, המילים מתחלפות
          </Typography>
        </DialogContent>
        <DialogActions sx={{ justifyContent: "center", gap: 1, pb: 2 }}>
          <Button
            variant="contained"
            onClick={handleReset}
            sx={{
              fontFamily: "'Fredoka', sans-serif",
              fontWeight: 600,
              borderRadius: 3,
              px: 3,
              bgcolor: "#7c3aed",
              "&:hover": { bgcolor: "#6d28d9" },
            }}
          >
            יאללה!
          </Button>
          <Button
            onClick={() => setResetOpen(false)}
            sx={{
              fontFamily: "'Fredoka', sans-serif",
              fontWeight: 600,
              borderRadius: 3,
              px: 3,
              color: "text.secondary",
            }}
          >
            ביטול
          </Button>
        </DialogActions>
      </Dialog>

    </Box>
  );
}
