import { useState } from "react";
import Header from "../components/Header";
import Sidebar from "../components/Sidebar";
import MapView from "../components/MapView";
import PromptBar from "../components/PromptBar";
import SatelliteLoader from "../components/SatelliteLoader";
import { queryBackend, type QueryResponse } from "../utils/api";
import type { User } from "../utils/auth";

interface DashboardProps {
  onBack: () => void;
  user?: User | null;
  onLogout?: () => void;
}

/**
 * Dashboard — Main SPA view
 *
 * Glass aesthetic over a satellite map.
 * Sidebar streams generative widgets from the Orbital Fusion backend.
 */
export default function Dashboard({ onBack, user, onLogout }: DashboardProps) {
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
    <div className="h-screen flex flex-col bg-bg text-text">
      {/* Satellite loading overlay */}
      {loading && <SatelliteLoader />}

      {/* Top header — glass style, with back button */}
      <Header onBack={onBack} user={user} onLogout={onLogout} />

      {/* Main content area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left sidebar — dashboard widgets */}
        <Sidebar response={response} loading={loading} />

        {/* Center — map + overlays */}
        <main className="flex-1 relative">
          <MapView
            lat={response?.fused_data.lat}
            lon={response?.fused_data.lon}
            regionName={response?.fused_data.region}
          />

          {/* Guidance text overlay */}
          {response && (
            <div className="absolute top-4 right-4 max-w-md glass-card rounded-xl p-4 z-[1000]">
              <div className="flex items-center gap-2 mb-2">
                <p className="text-xs text-primary font-semibold uppercase tracking-wider">
                  {response.intent.replace("_", " ")}
                </p>
                {response.ai_powered && (
                  <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest bg-gradient-to-r from-primary/20 to-accent/20 border border-primary/30 rounded-full text-primary">
                    ✦ Gemini AI
                  </span>
                )}
              </div>
              <p className="text-sm text-sage leading-relaxed whitespace-pre-line">
                {response.guidance_text}
              </p>
            </div>
          )}

          {/* Error banner */}
          {error && (
            <div className="absolute top-4 right-4 max-w-md bg-red-100 border-2 border-red-900 shadow-neo p-4 z-[1000]">
              <p className="text-sm text-red-900 font-bold">{error}</p>
            </div>
          )}
        </main>
      </div>

      {/* Bottom prompt bar */}
      <PromptBar onSubmit={handleQuery} loading={loading} />
    </div>
  );
}
