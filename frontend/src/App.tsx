import { BrowserRouter, Routes, Route, useParams } from "react-router-dom";
import { AppProvider } from "@/context/AppContext";
import Layout from "@/components/Layout";
import Welcome from "@/pages/Welcome";
import SubjectPicker from "@/pages/SubjectPicker";
import SessionPicker from "@/pages/SessionPicker";
import TopicSessions from "@/pages/TopicSessions";
import GameMenu from "@/pages/GameMenu";
import GameScreen from "@/games/english/GameScreen";
import MathGameScreen from "@/games/math/MathGameScreen";

/** Routes to the correct game screen based on subject param. */
function GameRouter() {
  const { subject } = useParams<{ subject: string }>();
  return subject === "math" ? <MathGameScreen /> : <GameScreen />;
}

// In production (FastAPI), React is served under /app/. In dev (Vite), at /.
const basename = import.meta.env.BASE_URL.replace(/\/$/, "") || "/";

export default function App() {
  return (
    <BrowserRouter basename={basename}>
      <AppProvider>
        <Routes>
          {/* Welcome — standalone, no header */}
          <Route path="/" element={<Welcome />} />

          {/* All other screens — wrapped in Layout with header */}
          <Route element={<Layout />}>
            <Route path="/learning" element={<SubjectPicker />} />
            <Route path="/learning/:subject" element={<SessionPicker />} />
            <Route path="/learning/:subject/topic/:topicSlug" element={<TopicSessions />} />
            <Route path="/learning/:subject/:sessionSlug" element={<GameMenu />} />
            <Route path="/learning/:subject/:sessionSlug/play/:gameId" element={<GameRouter />} />
          </Route>
        </Routes>
      </AppProvider>
    </BrowserRouter>
  );
}
