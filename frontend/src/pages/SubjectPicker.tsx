/**
 * Subject picker — choose English or Math.
 * Wrapped in Layout (header with stars + trophy, no home button).
 */

import { useNavigate } from "react-router-dom";
import { Box, Card, CardActionArea, Stack, Typography } from "@mui/material";

const SUBJECTS = [
  {
    id: "english",
    name: "אנגלית",
    icon: "/input-letters-light.svg",
    iconAlt: "אנגלית",
    iconClass: "english-icon",
  },
  {
    id: "math",
    name: "חשבון",
    icon: "/input-numbers-light.svg",
    iconAlt: "חשבון",
    iconClass: "math-icon",
  },
];

export default function SubjectPicker() {
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        px: 3,
        py: { xs: 4, sm: 6 },
      }}
    >
      {/* Title */}
      <Typography
        variant="h4"
        sx={{
          fontWeight: 700,
          mb: 4,
          animation: "bounceIn 0.6s ease-out",
          fontSize: { xs: "1.6rem", sm: "2rem" },
        }}
      >
        מה לומדים היום? 📚
      </Typography>

      {/* Subject cards */}
      <Stack spacing={3} sx={{ width: "100%", maxWidth: 420 }}>
        {SUBJECTS.map((subject, i) => (
          <Card
            key={subject.id}
            sx={{
              borderRadius: 4,
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
              onClick={() => navigate(`/learning/${subject.id}`)}
              sx={{
                display: "flex",
                alignItems: "center",
                gap: 2.5,
                p: { xs: 2.5, sm: 4 },
                justifyContent: "flex-start",
              }}
            >
              <Box
                component="img"
                src={subject.icon}
                alt={subject.iconAlt}
                sx={{ width: { xs: 56, sm: 72 }, height: { xs: 56, sm: 72 } }}
              />
              <Typography
                variant="h5"
                sx={{
                  fontWeight: 600,
                  fontSize: { xs: "1.3rem", sm: "1.6rem" },
                }}
              >
                {subject.name}
              </Typography>
            </CardActionArea>
          </Card>
        ))}
      </Stack>
    </Box>
  );
}
