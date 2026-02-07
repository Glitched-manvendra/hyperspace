import { useState } from "react";
import Header from "../components/Header";
import Sidebar from "../components/Sidebar";
import MapView from "../components/MapView";
import PromptBar from "../components/PromptBar";
import SatelliteLoader from "../components/SatelliteLoader";
import { queryBackend, type QueryResponse } from "../utils/api";

interface DashboardProps {
  onBack: () => void;
}

/**
 * Dashboard — Main SPA view
 *
 * Glass aesthetic over a satellite map.
 * Sidebar streams generative widgets from the Orbital Fusion backend.
 */
export default function Dashboard({ onBack }: DashboardProps) {
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
    <div className="h-screen flex flex-col bg-background">
      {/* Satellite loading overlay */}
      {loading && <SatelliteLoader />}

      {/* Top header — glass style, with back button */}
      <Header onBack={onBack} />

      {/* Main content area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left sidebar — dashboard widgets */}
        <Sidebar response={response} loading={loading} />

        {/* Center — map + overlays */}
        <main className="flex-1 relative">
          <MapView />

          {/* Guidance text overlay — glass panel */}
          {response && (
            <div className="absolute top-4 right-4 max-w-md glass-panel rounded-xl p-4 shadow-xl z-[1000] border border-glass-border">
              <p className="text-xs text-primary font-semibold uppercase tracking-wider mb-1">
                {response.intent.replace("_", " ")}
              </p>
              <p className="text-sm text-gray-300 leading-relaxed">
                {response.guidance_text}
              </p>
            </div>
          )}

          {/* Error banner */}
          {error && (
            <div className="absolute top-4 right-4 max-w-md bg-red-900/70 backdrop-blur-md border border-red-500/30 rounded-xl p-4 z-[1000]">
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
