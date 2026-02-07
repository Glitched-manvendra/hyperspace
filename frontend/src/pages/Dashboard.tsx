import { useState, useCallback } from "react";
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
            onLocationSelect={handleLocationSelect}
            onMultiLocationSelect={handleMultiLocationSelect}
            extraMarkers={extraMarkers}
            loading={loading}
          />

          {/* Guidance text overlay */}
          {response && (
            <div className="absolute top-4 right-4 max-w-md glass-card rounded-xl p-4 z-[1000] max-h-[60vh] overflow-y-auto">
              <div className="flex items-center gap-2 mb-2">
                <p className="text-xs text-primary font-semibold uppercase tracking-wider">
                  {response.intent.replace("_", " ")}
                </p>
                {response.ai_powered && (
                  <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest bg-gradient-to-r from-primary/20 to-accent/20 border border-primary/30 rounded-full text-primary">
                    ✦ Gemini AI
                  </span>
                )}
                {multiResponses.length > 1 && (
                  <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest bg-accent/20 border border-accent/30 rounded-full text-accent">
                    {multiResponses.length} locations
                  </span>
                )}
              </div>

              {/* Multi-location: show tabs for each location */}
              {multiResponses.length > 1 ? (
                <div className="space-y-3">
                  {multiResponses.map((r, i) => (
                    <div
                      key={`${r.fused_data.lat}-${r.fused_data.lon}`}
                      className="p-2.5 rounded-lg border border-border/50 cursor-pointer hover:bg-primary/5 transition-colors"
                      onClick={() => setResponse(r)}
                    >
                      <p className="text-xs font-bold text-primary mb-1">
                        📍 {r.fused_data.region}
                      </p>
                      <p className="text-xs text-sage leading-relaxed line-clamp-3">
                        {r.guidance_text.slice(0, 200)}…
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-sage leading-relaxed whitespace-pre-line">
                  {response.guidance_text}
                </p>
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
