/**
 * Session picker — choose a learning unit within a subject.
 * Shows subject tabs at top.
 * For subjects with topics (math): shows topic cards → click navigates to topic sessions.
 * For subjects without topics (english): shows session cards directly.
 */

import { useNavigate, useParams } from "react-router-dom";
import { Box, Card, CardActionArea, Stack, Tab, Tabs, Typography } from "@mui/material";
import { useApp } from "@/context/AppContext";

const SUBJECT_TABS = [
  { id: "english", label: "אנגלית", icon: "/static/input-letters-light.svg" },
  { id: "math", label: "חשבון", icon: "/static/input-numbers-light.svg" },
];

export default function SessionPicker() {
  const { subject } = useParams<{ subject: string }>();
  const navigate = useNavigate();
  const { sessionsBySubject, topicsBySubject, starsBySession, completedSessions } = useApp();

  const currentSubject = subject || "english";
  const topics = topicsBySubject[currentSubject] || [];
  const hasTopics = topics.length > 0;
  const sessions = sessionsBySubject[currentSubject] || [];

  const handleTabChange = (_: React.SyntheticEvent, newValue: string) => {
    navigate(`/learning/${newValue}`);
  };

  // Sum stars across all sessions in a topic
  const getTopicStars = (sessionSlugs: string[]): number =>
    sessionSlugs.reduce((sum, slug) => sum + (starsBySession[slug] || 0), 0);

  // Check if all sessions in a topic are completed
  const isTopicCompleted = (sessionSlugs: string[]): boolean =>
    sessionSlugs.length > 0 && sessionSlugs.every((slug) => completedSessions.includes(slug));

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
        בחרי שיעור
      </Typography>

      {/* Topic cards (for subjects with topics like math) */}
      {hasTopics && (
        <Stack spacing={2} sx={{ width: "100%", maxWidth: 500 }}>
          {topics.map((topic, i) => {
            const stars = getTopicStars(topic.session_slugs);
            const completed = isTopicCompleted(topic.session_slugs);

            return (
              <Card
                key={topic.slug}
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
                  onClick={() => navigate(`/learning/${currentSubject}/topic/${topic.slug}`)}
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    gap: 2,
                    p: { xs: 2, sm: 3 },
                    justifyContent: "flex-start",
                  }}
                >
                  <Typography sx={{ fontSize: "2.2rem", minWidth: 48, textAlign: "center" }}>
                    {topic.emoji}
                  </Typography>
                  <Box sx={{ flex: 1 }}>
                    <Typography
                      variant="h6"
                      sx={{ fontWeight: 600, fontSize: { xs: "1rem", sm: "1.15rem" } }}
                    >
                      {topic.name_he}
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
      )}

      {/* Session cards (for subjects without topics like english) */}
      {!hasTopics && (
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
      )}

      {/* Empty state */}
      {!hasTopics && sessions.length === 0 && (
        <Typography variant="body1" color="text.secondary" sx={{ mt: 4 }}>
          אין שיעורים עדיין
        </Typography>
      )}
    </Box>
  );
}
