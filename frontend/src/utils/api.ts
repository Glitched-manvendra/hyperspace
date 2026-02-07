import axios from "axios";

/** UI card instruction from the backend */
export interface UIInstruction {
  card_type: string;
  title: string;
  value: string;
  subtitle: string;
  color: string;
  /** Rich data payload for generative widgets (charts, lists, etc.) */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data?: Record<string, any>;
}

/** Fused satellite data summary */
export interface FusedDataSummary {
  region: string;
  lat: number;
  lon: number;
  temperature_avg_c: number;
  rainfall_mm: number;
  soil_moisture_pct: number;
  ndvi_avg: number;
  data_sources: string[];
}

/** Full query response from the backend */
export interface QueryResponse {
  intent: string;
  query_echo: string;
  fused_data: FusedDataSummary;
  guidance_text: string;
  ai_powered: boolean;
  recommendations: Array<{
    crop_name: string;
    confidence: number;
    reasoning: string;
    season: string;
  }>;
  ui_instructions: UIInstruction[];
}

/** Backend API base URL — proxied through Vite in development */
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Send a natural language query to the backend.
 *
 * @param query - The user's question about satellite data
 * @param lat - Latitude (default: Greater Noida)
 * @param lon - Longitude (default: Greater Noida)
 * @returns Structured query response with fused data and UI instructions
 */
export async function queryBackend(
  query: string,
  lat = 28.4744,
  lon = 77.504,
): Promise<QueryResponse> {
  const res = await axios.post<QueryResponse>(`${API_BASE}/api/query`, {
    query,
    lat,
    lon,
  });
  return res.data;
}
