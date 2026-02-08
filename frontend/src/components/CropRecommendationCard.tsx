import { Thermometer, Droplets, Sprout, TrendingUp } from "lucide-react";
import type { QueryResponse } from "../utils/api";

interface CropRecommendationCardProps {
  response: QueryResponse;
  multiResponses?: QueryResponse[];
  onSelectLocation?: (response: QueryResponse) => void;
}

/**
 * Clean, modern crop recommendation card
 * Centered layout with professional agricultural-tech aesthetic
 */
export default function CropRecommendationCard({
  response,
  multiResponses = [],
  onSelectLocation,
}: CropRecommendationCardProps) {
  const { fused_data, guidance_text, intent, ai_powered } = response;

  // Extract key metrics from the guidance text
  const extractMetric = (text: string, keyword: string): string => {
    const regex = new RegExp(`${keyword}[:\\s]+([^,\\.\\n]+)`, "i");
    const match = text.match(regex);
    return match ? match[1].trim() : "N/A";
  };

  const temperature = extractMetric(guidance_text, "temperature");
  const soilMoisture = extractMetric(guidance_text, "soil moisture");
  const ndvi = extractMetric(guidance_text, "ndvi");

  // Extract crop recommendation (usually in the guidance text)
  const cropMatch = guidance_text.match(/recommends?:?\s*([^\.]+)/i);
  const cropRecommendation = cropMatch ? cropMatch[1].trim() : "See details below";

  return (
    <div className="recommendation-card max-w-3xl mx-auto p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-green-900 mb-1">
            Crop Recommendation
          </h1>
          <p className="text-sm text-green-700 font-medium">
            📍 {fused_data.region}
          </p>
        </div>
        <div className="flex gap-2">
          {ai_powered && (
            <span className="px-3 py-1.5 text-xs font-bold uppercase tracking-wider bg-gradient-to-r from-green-100 to-emerald-100 border-2 border-green-300 rounded-lg text-green-800">
              ✦ AI-Powered
            </span>
          )}
          {multiResponses.length > 1 && (
            <span className="px-3 py-1.5 text-xs font-bold uppercase tracking-wider bg-blue-100 border-2 border-blue-300 rounded-lg text-blue-800">
              {multiResponses.length} Locations
            </span>
          )}
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {/* Temperature */}
        <div className="metric-card">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Thermometer className="w-5 h-5 text-orange-600" />
            </div>
            <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wide">
              Temperature
            </h3>
          </div>
          <p className="text-2xl font-bold text-gray-900">{temperature}</p>
        </div>

        {/* Soil Moisture */}
        <div className="metric-card">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Droplets className="w-5 h-5 text-blue-600" />
            </div>
            <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wide">
              Soil Moisture
            </h3>
          </div>
          <p className="text-2xl font-bold text-gray-900">{soilMoisture}</p>
        </div>

        {/* NDVI */}
        <div className="metric-card">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-green-100 rounded-lg">
              <Sprout className="w-5 h-5 text-green-600" />
            </div>
            <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wide">
              NDVI Index
            </h3>
          </div>
          <p className="text-2xl font-bold text-gray-900">{ndvi}</p>
        </div>

        {/* Crop Recommendation */}
        <div className="metric-card">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-emerald-100 rounded-lg">
              <TrendingUp className="w-5 h-5 text-emerald-600" />
            </div>
            <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wide">
              Recommended Crop
            </h3>
          </div>
          <p className="text-2xl font-bold text-green-900">{cropRecommendation}</p>
        </div>
      </div>

      {/* Multi-location selector */}
      {multiResponses.length > 1 && (
        <div className="mb-6">
          <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wide mb-3">
            Other Locations
          </h3>
          <div className="grid grid-cols-1 gap-2">
            {multiResponses.map((r, i) => (
              <button
                key={`${r.fused_data.lat}-${r.fused_data.lon}`}
                onClick={() => onSelectLocation?.(r)}
                className="p-3 rounded-lg border-2 border-green-200 hover:border-green-400 hover:bg-green-50 transition-all text-left"
              >
                <p className="text-sm font-bold text-green-900">
                  📍 {r.fused_data.region}
                </p>
                <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                  {r.guidance_text.slice(0, 150)}...
                </p>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Full Analysis */}
      <div className="mt-6 pt-6 border-t-2 border-green-100">
        <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wide mb-3">
          AI Crop Brain Analysis
        </h3>
        <div className="bg-gradient-to-br from-gray-50 to-green-50 rounded-xl p-5 border border-gray-200">
          <p className="text-sm text-gray-800 leading-relaxed whitespace-pre-line">
            {guidance_text}
          </p>
        </div>
      </div>

      {/* Intent Badge */}
      <div className="mt-4 flex justify-center">
        <span className="px-3 py-1 text-xs font-semibold uppercase tracking-wider text-green-700 bg-green-100 rounded-full">
          {intent.replace("_", " ")}
        </span>
      </div>
    </div>
  );
}
