import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppProvider } from "@/context/AppContext";
import Layout from "@/components/Layout";
import Welcome from "@/pages/Welcome";
import SubjectPicker from "@/pages/SubjectPicker";
import SessionPicker from "@/pages/SessionPicker";
import GameMenu from "@/pages/GameMenu";
import GameScreen from "@/games/english/GameScreen";

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
            <Route path="/learning/:subject/:sessionSlug" element={<GameMenu />} />
            <Route path="/learning/:subject/:sessionSlug/play/:gameId" element={<GameScreen />} />
          </Route>
        </Routes>
      </AppProvider>
    </BrowserRouter>
  );
}
