/**
 * GameScreen — route wrapper that manages the session plan and renders
 * the correct game component based on URL params.
 *
 * URL: /learning/:subject/:sessionSlug/play/:gameId
 */

import { lazy, Suspense, useEffect, useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Box, CircularProgress, IconButton, Typography } from "@mui/material";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import { getUnitData, planSession, GAME_TYPE_MAP } from "@/data/english";
import type { SessionPlan } from "@/data/english";
import { saveGameResult, getPracticedWords } from "@/api/game";
import { useApp } from "@/context/AppContext";
import type { WordResult } from "@/api/types";
import { ENGLISH_GAMES } from "@/data/games";

const WordMatch = lazy(() => import("./WordMatch"));
const SentenceScramble = lazy(() => import("./SentenceScramble"));
const ListenAndChoose = lazy(() => import("./ListenAndChoose"));
const TrueFalse = lazy(() => import("./TrueFalse"));
const CompletionScreen = lazy(() => import("./CompletionScreen"));

const SS_PLAN_KEY = "ariel_session_plan";
const SS_COMPLETED_KEY = "ariel_session_completed_games";

/** Load or create a session plan, cached in sessionStorage */
function getOrCreatePlan(sessionSlug: string): SessionPlan {
  const cacheKey = `${SS_PLAN_KEY}_${sessionSlug}`;
  const cached = sessionStorage.getItem(cacheKey);
  if (cached) {
    try {
      return JSON.parse(cached) as SessionPlan;
    } catch {
      // Corrupted cache — regenerate
    }
  }
  const unit = getUnitData(sessionSlug);
  const plan = planSession(unit.vocabulary, unit.scrambleSentences, unit.trueFalseSentences);
  sessionStorage.setItem(cacheKey, JSON.stringify(plan));
  return plan;
}

/** Load completed game set from sessionStorage */
function getCompletedGames(sessionSlug: string): Set<number> {
  try {
    const raw = sessionStorage.getItem(`${SS_COMPLETED_KEY}_${sessionSlug}`);
    return new Set(raw ? (JSON.parse(raw) as number[]) : []);
  } catch {
    return new Set();
  }
}

/** Save completed game to sessionStorage */
function markGameCompleted(sessionSlug: string, gameId: number): void {
  const completed = getCompletedGames(sessionSlug);
  completed.add(gameId);
  sessionStorage.setItem(
    `${SS_COMPLETED_KEY}_${sessionSlug}`,
    JSON.stringify([...completed]),
  );
}

export default function GameScreen() {
  const { subject, sessionSlug, gameId: gameIdParam } = useParams<{
    subject: string;
    sessionSlug: string;
    gameId: string;
  }>();
  const navigate = useNavigate();
  const { refreshProgress } = useApp();
  const slug = sessionSlug || "jet2-unit2";
  const gameId = parseInt(gameIdParam || "1", 10);
  const unit = getUnitData(slug);

  const plan = useMemo(() => getOrCreatePlan(slug), [slug]);
  const [practicedWords, setPracticedWords] = useState<Set<string>>(new Set());
  const [finished, setFinished] = useState(false);
  const [finalScore, setFinalScore] = useState(0);
  const [finalMax, setFinalMax] = useState(0);

  // Load practiced words on mount
  useEffect(() => {
    getPracticedWords(slug).then((res) => {
      if (res.success) {
        setPracticedWords(new Set(res.data.practiced_words));
      }
    }).catch(() => {});
  }, [slug]);

  const gameInfo = ENGLISH_GAMES.find((g) => g.id === gameId);
  const gameTitle = gameInfo?.title || "";

  const handleFinish = async (
    score: number,
    maxScore: number,
    wordResults: WordResult[],
  ) => {
    setFinalScore(score);
    setFinalMax(maxScore);
    setFinished(true);

    // Mark game completed in session
    markGameCompleted(slug, gameId);

    // Update practiced words locally
    const newPracticed = new Set(practicedWords);
    wordResults.forEach((r) => newPracticed.add(r.word.toLowerCase()));
    setPracticedWords(newPracticed);

    // Save to API
    const gameType = GAME_TYPE_MAP[gameId];
    if (gameType) {
      try {
        await saveGameResult({
          game_type: gameType,
          score,
          max_score: maxScore,
          word_results: wordResults,
          session_slug: slug,
        });
        await refreshProgress();
      } catch (err) {
        console.error("Failed to save game result:", err);
      }
    }
  };

  const handleReplay = () => {
    setFinished(false);
    setFinalScore(0);
    setFinalMax(0);
  };

  const handleBackToMenu = () => {
    navigate(`/learning/${subject}/${slug}`);
  };

  const suspenseFallback = (
    <Box sx={{ display: "flex", justifyContent: "center", py: 8 }}>
      <CircularProgress />
    </Box>
  );

  if (finished) {
    return (
      <Suspense fallback={suspenseFallback}>
        <CompletionScreen
          score={finalScore}
          maxScore={finalMax}
          onReplay={handleReplay}
          onBackToMenu={handleBackToMenu}
        />
      </Suspense>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "calc(100vh - 72px)" }}>
      {/* Game header */}
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 1,
          px: { xs: 2, sm: 3 },
          pt: 2,
          pb: 1,
        }}
      >
        <IconButton onClick={handleBackToMenu} size="small">
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
          {gameTitle}
        </Typography>
        {/* Spacer to center title */}
        <Box sx={{ width: 34 }} />
      </Box>

      {/* Game content */}
      <Suspense fallback={suspenseFallback}>
        <Box sx={{ flex: 1, display: "flex", flexDirection: "column" }}>
          {gameId === 1 && (
            <WordMatch
              words={plan.game1Words}
              vocabulary={unit.vocabulary}
              onFinish={handleFinish}
            />
          )}
          {gameId === 2 && (
            <SentenceScramble
              sentences={plan.game2Sentences}
              vocabulary={unit.vocabulary}
              onFinish={handleFinish}
            />
          )}
          {gameId === 3 && (
            <ListenAndChoose
              words={plan.game3Words}
              vocabulary={unit.vocabulary}
              onFinish={handleFinish}
            />
          )}
          {gameId === 4 && (
            <TrueFalse
              sentences={plan.game4Sentences}
              vocabulary={unit.vocabulary}
              onFinish={handleFinish}
            />
          )}
        </Box>
      </Suspense>
    </Box>
  );
}
