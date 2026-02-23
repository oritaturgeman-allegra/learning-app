/**
 * MathGameScreen — route wrapper that renders the correct math game
 * based on URL params and handles result saving.
 *
 * URL: /learning/math/:sessionSlug/play/:gameId
 */

import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Box, IconButton, Typography } from "@mui/material";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import { saveGameResult } from "@/api/game";
import { useApp } from "@/context/AppContext";
import { MATH_GAME_TYPE_MAP } from "@/data/math";
import { MATH_GAMES } from "@/data/games";
import type { WordResult } from "@/api/types";
import CompletionScreen from "@/games/english/CompletionScreen";
import QuickSolve from "./QuickSolve";
import MissingNumber from "./MissingNumber";
import MathTrueFalse from "./MathTrueFalse";
import BubblePop from "./BubblePop";

const SS_COMPLETED_KEY = "ariel_session_completed_games";

function markGameCompleted(sessionSlug: string, gameId: number): void {
  try {
    const raw = sessionStorage.getItem(`${SS_COMPLETED_KEY}_${sessionSlug}`);
    const completed = new Set<number>(raw ? (JSON.parse(raw) as number[]) : []);
    completed.add(gameId);
    sessionStorage.setItem(
      `${SS_COMPLETED_KEY}_${sessionSlug}`,
      JSON.stringify([...completed]),
    );
  } catch {
    // Ignore storage errors
  }
}

export default function MathGameScreen() {
  const { sessionSlug, gameId: gameIdParam } = useParams<{
    sessionSlug: string;
    gameId: string;
  }>();
  const navigate = useNavigate();
  const { refreshProgress } = useApp();
  const slug = sessionSlug || "math-tens-hundreds";
  const gameId = parseInt(gameIdParam || "1", 10);

  const [finished, setFinished] = useState(false);
  const [finalScore, setFinalScore] = useState(0);
  const [finalMax, setFinalMax] = useState(0);

  const gameInfo = MATH_GAMES.find((g) => g.id === gameId);
  const gameTitle = gameInfo?.title || "";

  const handleFinish = async (
    score: number,
    maxScore: number,
    wordResults: WordResult[],
  ) => {
    setFinalScore(score);
    setFinalMax(maxScore);
    setFinished(true);

    markGameCompleted(slug, gameId);

    const gameType = MATH_GAME_TYPE_MAP[gameId];
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
        console.error("Failed to save math game result:", err);
      }
    }
  };

  const handleReplay = () => {
    setFinished(false);
    setFinalScore(0);
    setFinalMax(0);
  };

  const handleBackToMenu = () => {
    navigate(`/learning/math/${slug}`);
  };

  if (finished) {
    return (
      <CompletionScreen
        score={finalScore}
        maxScore={finalMax}
        onReplay={handleReplay}
        onBackToMenu={handleBackToMenu}
      />
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
        <Box sx={{ width: 34 }} />
      </Box>

      {/* Game content */}
      <Box sx={{ flex: 1, display: "flex", flexDirection: "column" }}>
        {gameId === 1 && (
          <QuickSolve sessionSlug={slug} onFinish={handleFinish} />
        )}
        {gameId === 2 && (
          <MissingNumber sessionSlug={slug} onFinish={handleFinish} />
        )}
        {gameId === 3 && (
          <MathTrueFalse sessionSlug={slug} onFinish={handleFinish} />
        )}
        {gameId === 4 && (
          <BubblePop sessionSlug={slug} onFinish={handleFinish} />
        )}
      </Box>
    </Box>
  );
}
