import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { Box, Container, Typography, Button } from "@mui/material";

// Placeholder pages — replaced with real components in Phase 3
function Welcome() {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #a855f7, #ec4899, #f97316)",
        textAlign: "center",
        p: 3,
      }}
    >
      <Typography variant="h2" sx={{ color: "white", mb: 2 }}>
        🎮
      </Typography>
      <Typography variant="h3" sx={{ color: "white", fontWeight: 700, mb: 1 }}>
        !הי אריאל
      </Typography>
      <Typography variant="h6" sx={{ color: "rgba(255,255,255,0.9)", mb: 4 }}>
        ?מוכנה ללמוד ולהרוויח כוכבים
      </Typography>
      <Button
        variant="contained"
        size="large"
        component={Link}
        to="/learning"
        sx={{
          bgcolor: "white",
          color: "#a855f7",
          fontWeight: 700,
          fontSize: "1.2rem",
          px: 5,
          py: 1.5,
          "&:hover": { bgcolor: "rgba(255,255,255,0.9)" },
        }}
      >
        יאללה!
      </Button>
    </Box>
  );
}

function SubjectPicker() {
  return (
    <Container maxWidth="sm" sx={{ py: 6, textAlign: "center" }}>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 700 }}>
        ?מה לומדים היום
      </Typography>
      <Box sx={{ display: "flex", gap: 3, justifyContent: "center", flexWrap: "wrap" }}>
        <Button variant="contained" component={Link} to="/learning/english" size="large" sx={{ px: 4, py: 2, fontSize: "1.1rem" }}>
          📘 אנגלית
        </Button>
        <Button variant="contained" component={Link} to="/learning/math" size="large" sx={{ px: 4, py: 2, fontSize: "1.1rem", bgcolor: "#3b82f6" }}>
          🔢 חשבון
        </Button>
      </Box>
    </Container>
  );
}

function SessionPicker() {
  return (
    <Container maxWidth="sm" sx={{ py: 6, textAlign: "center" }}>
      <Typography variant="h4" sx={{ mb: 2, fontWeight: 700 }}>
        בחרי שיעור
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Placeholder — Session cards come in Phase 3
      </Typography>
    </Container>
  );
}

function GameMenu() {
  return (
    <Container maxWidth="sm" sx={{ py: 6, textAlign: "center" }}>
      <Typography variant="h4" sx={{ mb: 2, fontWeight: 700 }}>
        בחרי משחק
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Placeholder — Game cards come in Phase 3
      </Typography>
    </Container>
  );
}

// In production (FastAPI), React is served under /app/. In dev (Vite), at /.
const basename = import.meta.env.BASE_URL.replace(/\/$/, "") || "/";

export default function App() {
  return (
    <BrowserRouter basename={basename}>
      <Routes>
        <Route path="/" element={<Welcome />} />
        <Route path="/learning" element={<SubjectPicker />} />
        <Route path="/learning/:subject" element={<SessionPicker />} />
        <Route path="/learning/:subject/:sessionSlug" element={<GameMenu />} />
      </Routes>
    </BrowserRouter>
  );
}
