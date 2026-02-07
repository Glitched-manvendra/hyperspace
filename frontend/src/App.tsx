import { useState } from "react";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import MapView from "./components/MapView";
import PromptBar from "./components/PromptBar";
import LandingPage from "./pages/LandingPage";
import { queryBackend, type QueryResponse } from "./utils/api";

/**
 * Orbital Nexus — Root Application
 *
 * State-based navigation:
 *   "landing"   → Marketing / Landing page
 *   "dashboard" → Main SPA (Map + Sidebar + Prompt)
 */
type View = "landing" | "dashboard";

function App() {
  const [view, setView] = useState<View>("landing");

  if (view === "landing") {
    return <LandingPage onLaunch={() => setView("dashboard")} />;
  }

  return <Dashboard onBack={() => setView("landing")} />;
}

/* ═══════════════════════════════════════════════════════════════════
   DASHBOARD — the existing SPA, extracted into its own component
   ═══════════════════════════════════════════════════════════════════ */
function Dashboard({ onBack }: { onBack: () => void }) {
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleQuery = async (query: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await queryBackend(query);
      setResponse(data);
    } catch (err) {
      setError("Failed to connect to backend. Is it running on port 8000?");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-nexus-dark">
      {/* Top header — with back button */}
      <Header onBack={onBack} />

      {/* Main content area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left sidebar — dashboard cards */}
        <Sidebar response={response} loading={loading} />

        {/* Center — map + guidance overlay */}
        <main className="flex-1 relative">
          <MapView />

          {/* Guidance text overlay */}
          {response && (
            <div className="absolute top-4 right-4 max-w-md bg-nexus-panel/90 backdrop-blur border border-gray-700 rounded-lg p-4 shadow-xl z-[1000]">
              <p className="text-xs text-nexus-glow font-medium uppercase tracking-wider mb-1">
                {response.intent.replace("_", " ")}
              </p>
              <p className="text-sm text-gray-300 leading-relaxed">
                {response.guidance_text}
              </p>
            </div>
          )}

          {/* Error banner */}
          {error && (
            <div className="absolute top-4 right-4 max-w-md bg-red-900/80 border border-red-600 rounded-lg p-4 z-[1000]">
              <p className="text-sm text-red-200">{error}</p>
            </div>
          )}
        </main>
      </div>

      {/* Bottom prompt bar */}
      <PromptBar onSubmit={handleQuery} loading={loading} />
    </div>
  );
}

export default App;
