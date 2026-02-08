import { useState, useCallback, useEffect } from "react";
import Header from "../components/Header";
import Sidebar from "../components/Sidebar";
import MapView from "../components/MapView";
import PromptBar from "../components/PromptBar";
import SatelliteLoader from "../components/SatelliteLoader";
import { queryBackend, multiQueryBackend, type QueryResponse } from "../utils/api";
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
 * Supports multi-location queries (e.g., "NDVI for Agra and Mathura").
 */
export default function Dashboard({ onBack, user, onLogout }: DashboardProps) {
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [multiResponses, setMultiResponses] = useState<QueryResponse[]>([]);
  const [extraMarkers, setExtraMarkers] = useState<{ lat: number; lon: number; name: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Resize State
  const [sidebarWidth, setSidebarWidth] = useState(320);
  const [isResizing, setIsResizing] = useState(false);

  /** Handle resize start */
  const startResizing = useCallback(() => {
    setIsResizing(true);
  }, []);

  /** Handle resize stop */
  const stopResizing = useCallback(() => {
    setIsResizing(false);
  }, []);

  /** Handle mouse move during resize */
  const resizeHandler = useCallback(
    (e: MouseEvent) => {
      if (isResizing) {
        const newWidth = e.clientX;
        // Constraints: 240px to 600px
        if (newWidth >= 240 && newWidth <= 600) {
          setSidebarWidth(newWidth);
        }
      }
    },
    [isResizing]
  );

  // Attach/Detach event listeners for smooth resizing outside the handle
  useEffect(() => {
    if (isResizing) {
      window.addEventListener("mousemove", resizeHandler);
      window.addEventListener("mouseup", stopResizing);
    } else {
      window.removeEventListener("mousemove", resizeHandler);
      window.removeEventListener("mouseup", stopResizing);
    }
    return () => {
      window.removeEventListener("mousemove", resizeHandler);
      window.removeEventListener("mouseup", stopResizing);
    };
  }, [isResizing, resizeHandler, stopResizing]);

  /** Run a natural-language query (from the prompt bar) — supports multi-city */
  const handleQuery = async (query: string) => {
    setLoading(true);
    setError(null);
    setExtraMarkers([]);
    setMultiResponses([]);
    try {
      // Use multi-query endpoint so multi-city queries work
      const results = await multiQueryBackend(query);
      if (results.length === 0) {
        setError("No data found for this query. Try a different location.");
      } else if (results.length === 1) {
        setResponse(results[0]);
        setMultiResponses([]);
        setExtraMarkers([]);
      } else {
        // Multi-location: show first in main view, all as markers
        setResponse(results[0]);
        setMultiResponses(results);
        setExtraMarkers(
          results.map((r) => ({
            lat: r.fused_data.lat,
            lon: r.fused_data.lon,
            name: r.fused_data.region,
          }))
        );
      }
    } catch (err) {
      setError("Failed to connect to backend. Is it running on port 8000?");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  /** Run a coordinate-based query (from map click / search) */
  const handleLocationSelect = useCallback(
    async (lat: number, lon: number, name?: string) => {
      setLoading(true);
      setError(null);
      setExtraMarkers([]);
      setMultiResponses([]);
      try {
        const locationLabel = name ?? `${lat.toFixed(2)}°N, ${lon.toFixed(2)}°E`;
        const query = `Give me a complete crop and soil analysis for ${locationLabel}`;
        const data = await queryBackend(query, lat, lon);
        setResponse(data);
      } catch (err) {
        setError("Failed to fetch data for this location. Please try again.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  /** Handle multi-city search from map search bar */
  const handleMultiLocationSelect = useCallback(
    async (locations: { lat: number; lon: number; name: string }[]) => {
      setLoading(true);
      setError(null);
      setExtraMarkers(locations);
      setMultiResponses([]);
      try {
        const names = locations.map((l) => l.name.split(",")[0]).join(" and ");
        const query = `Give me crop and soil analysis for ${names}`;
        const results = await multiQueryBackend(query);
        if (results.length > 0) {
          setResponse(results[0]);
          setMultiResponses(results);
          setExtraMarkers(
            results.map((r) => ({
              lat: r.fused_data.lat,
              lon: r.fused_data.lon,
              name: r.fused_data.region,
            }))
          );
        }
      } catch (err) {
        setError("Failed to fetch data for these locations. Please try again.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return (
    <div className={`h-screen flex flex-col bg-bg text-text ${isResizing ? 'select-none cursor-col-resize' : ''}`}>
      {/* Satellite loading overlay */}
      {loading && <SatelliteLoader />}

      {/* Top header — glass style, with back button */}
      <Header onBack={onBack} user={user} onLogout={onLogout} />

      {/* Main content area */}
      <div className="flex flex-1 overflow-hidden relative">
        {/* Left sidebar — dashboard widgets */}
        <Sidebar response={response} loading={loading} width={sidebarWidth} />

        {/* Resize Handle */}
        <div
          onMouseDown={startResizing}
          className={`absolute top-0 bottom-0 z-30 w-1.5 cursor-col-resize transition-colors hover:bg-primary/40 active:bg-primary ${isResizing ? 'bg-primary' : 'bg-transparent'}`}
          style={{ left: sidebarWidth - 3 }}
        />

        {/* Center — map + overlays */}
        <main className="flex-1 relative">
          <MapView
            lat={response?.fused_data.lat}
            lon={response?.fused_data.lon}
            regionName={response?.fused_data.region}
            onLocationSelect={handleLocationSelect}
            onMultiLocationSelect={handleMultiLocationSelect}
            extraMarkers={extraMarkers}
            loading={loading}
          />

          {/* Guidance text overlay */}
          {response && (
            <div className="absolute top-4 right-4 max-w-sm bg-black/20 backdrop-blur-md rounded-xl p-4 z-[1000] max-h-[70vh] overflow-y-auto shadow-lg border border-white/20">
              {/* Header */}
              <div className="flex items-center justify-between mb-3 pb-2 border-b border-white/20">
                <div>
                  <p className="text-xs font-bold text-white uppercase tracking-wide">
                    {response.intent.replace("_", " ")}
                  </p>
                  <p className="text-[10px] text-white/80 mt-0.5">
                    📍 {response.fused_data.region}
                  </p>
                </div>
                {response.ai_powered && (
                  <span className="px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider bg-green-500/30 border border-green-400/50 rounded-md text-white">
                    ✦ AI
                  </span>
                )}
              </div>

              {/* Multi-location selector */}
              {multiResponses.length > 1 ? (
                <div className="space-y-2">
                  <p className="text-[10px] font-semibold text-white/90 uppercase tracking-wide mb-2">
                    Locations ({multiResponses.length}):
                  </p>
                  {multiResponses.map((r) => (
                    <button
                      key={`${r.fused_data.lat}-${r.fused_data.lon}`}
                      className="w-full p-2 rounded-lg border border-white/20 hover:border-green-400/50 hover:bg-white/10 transition-all text-left"
                      onClick={() => setResponse(r)}
                    >
                      <p className="text-xs font-bold text-white">
                        📍 {r.fused_data.region}
                      </p>
                    </button>
                  ))}
                </div>
              ) : (
                <div>
                  <p className="text-sm text-white leading-relaxed whitespace-pre-line line-clamp-6">
                    {response.guidance_text}
                  </p>
                </div>
              )}
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
