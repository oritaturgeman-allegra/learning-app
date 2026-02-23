/**
 * TopicSessions — shows sessions within a topic.
 * URL: /learning/:subject/topic/:topicSlug
 *
 * For math: shows 4 session cards (e.g., כפל בעשרות, כפל דו-ספרתי, etc.)
 * Clicking a session navigates to GameMenu.
 */

import { useNavigate, useParams } from "react-router-dom";
import { Box, Card, CardActionArea, IconButton, Stack, Typography } from "@mui/material";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import { useApp } from "@/context/AppContext";

export default function TopicSessions() {
  const { subject, topicSlug } = useParams<{ subject: string; topicSlug: string }>();
  const navigate = useNavigate();
  const { sessionsBySubject, topicsBySubject, starsBySession, completedSessions } = useApp();

  const currentSubject = subject || "math";
  const topics = topicsBySubject[currentSubject] || [];
  const topic = topics.find((t) => t.slug === topicSlug);
  const allSessions = sessionsBySubject[currentSubject] || [];

  // Filter sessions to only those in this topic
  const sessions = topic
    ? allSessions.filter((s) => topic.session_slugs.includes(s.slug))
    : [];

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
      {/* Header with back button */}
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
        <IconButton onClick={() => navigate(`/learning/${currentSubject}`)} size="small">
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
          {topic?.name_he || ""}
        </Typography>
        <Box sx={{ width: 34 }} />
      </Box>

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
        בחרי שיעור
      </Typography>

      {/* Session cards */}
      <Stack spacing={2} sx={{ width: "100%", maxWidth: 500 }}>
        {sessions.map((session, i) => {
          const stars = starsBySession[session.slug] || 0;
          const completed = completedSessions.includes(session.slug);

          return (
            <Card
              key={session.slug}
              sx={{
                borderRadius: 4,
                border: completed ? "2px solid #22c55e" : "2px solid transparent",
                boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
                animation: `slideUp 0.5s ease-out ${0.1 + i * 0.15}s both`,
                "&:hover": {
                  transform: "translateY(-4px)",
                  boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
                },
                transition: "transform 0.2s, box-shadow 0.2s",
              }}
            >
              <CardActionArea
                onClick={() => navigate(`/learning/${currentSubject}/${session.slug}`)}
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: 2,
                  p: { xs: 2, sm: 3 },
                  justifyContent: "flex-start",
                }}
              >
                <Typography sx={{ fontSize: "2.2rem", minWidth: 48, textAlign: "center" }}>
                  {session.emoji}
                </Typography>
                <Box sx={{ flex: 1 }}>
                  <Typography
                    variant="h6"
                    sx={{ fontWeight: 600, fontSize: { xs: "1rem", sm: "1.15rem" } }}
                  >
                    {currentSubject === "english" ? session.name : session.name_he}
                  </Typography>
                  <Box
                    sx={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 0.5,
                      bgcolor: "#fef3c7",
                      borderRadius: 9999,
                      px: 1.25,
                      py: 0.25,
                      mt: 0.5,
                    }}
                  >
                    <Typography component="span" sx={{ fontSize: "0.85rem" }}>
                      ⭐
                    </Typography>
                    <Typography
                      component="span"
                      sx={{
                        fontFamily: "'Fredoka', sans-serif",
                        fontWeight: 600,
                        fontSize: "0.85rem",
                        color: "#f59e0b",
                      }}
                    >
                      {stars}
                    </Typography>
                  </Box>
                </Box>
                {completed ? (
                  <Box
                    sx={{
                      width: 32,
                      height: 32,
                      borderRadius: "50%",
                      bgcolor: "#22c55e",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      color: "white",
                      fontWeight: 700,
                      fontSize: "1rem",
                      animation: "checkPop 0.4s ease-out",
                    }}
                  >
                    ✓
                  </Box>
                ) : (
                  <Typography
                    sx={{ fontSize: "1.4rem", color: "text.secondary", opacity: 0.5 }}
                  >
                    ←
                  </Typography>
                )}
              </CardActionArea>
            </Card>
          );
        })}
      </Stack>

      {sessions.length === 0 && (
        <Typography variant="body1" color="text.secondary" sx={{ mt: 4 }}>
          אין שיעורים בנושא הזה
        </Typography>
      )}
    </Box>
  );
}
