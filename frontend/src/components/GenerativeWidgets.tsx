/**
 * GenerativeWidgets — Server-Driven UI components
 *
 * These widgets are rendered dynamically based on `ui_instructions`
 * from the backend. The card_type field determines which widget
 * the WidgetFactory selects.
 *
 * Supported widgets:
 *   chart_line → PriceTrendChart  (recharts LineChart)
 *   chart_pie  → SoilCompositionChart (recharts PieChart)
 *   list       → RecommendationList (crop list with confidence)
 */

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  Legend,
} from "recharts";

/* ─── colour palette ─── */
const EMERALD = "#34d399";
const CYAN = "#22d3ee";
const BLUE = "#60a5fa";
const TEAL = "#2dd4bf";
const AMBER = "#fbbf24";
const ROSE = "#fb7185";

const PIE_COLORS = [EMERALD, CYAN, BLUE, TEAL, AMBER, ROSE];

/* ─── shared types ─── */
export interface WidgetData {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  [key: string]: any;
}

/* ═══════════════════════════════════════════════════════════════════
   PRICE TREND — Line Chart
   card_type: "chart_line"
   Expected data shape:
     data: { points: [{label, value}], unit?: string }
   ═══════════════════════════════════════════════════════════════════ */
interface PriceTrendProps {
  title: string;
  subtitle?: string;
  data?: WidgetData;
}

export function PriceTrendChart({ title, subtitle, data }: PriceTrendProps) {
  // Normalise: backend may send {label,value} or {month,...multi-series}
  let points: { label: string; value: number }[] = [];
  if (data?.points && data.points.length > 0) {
    const first = data.points[0];
    if ("label" in first && "value" in first) {
      // Simple single-line format
      points = data.points;
    } else if ("month" in first) {
      // Multi-series format — flatten to first series value
      const seriesKeys = Object.keys(first).filter((k) => k !== "month");
      const key = seriesKeys[0] ?? "value";
      points = data.points.map((p: Record<string, unknown>) => ({
        label: String(p.month ?? ""),
        value: Number(p[key] ?? 0),
      }));
    } else {
      points = data.points;
    }
  }
  if (points.length === 0) {
    points = [
      { label: "Jan", value: 1200 },
      { label: "Feb", value: 1350 },
      { label: "Mar", value: 1100 },
      { label: "Apr", value: 980 },
      { label: "May", value: 1450 },
      { label: "Jun", value: 1600 },
    ];
  }
  const unit: string = data?.unit ?? "₹/qtl";

  return (
    <div className="neo-box p-4 bg-surface">
      <p className="text-[11px] text-text/60 uppercase tracking-widest font-bold mb-0.5">
        {title}
      </p>
      {subtitle && (
        <p className="text-[10px] text-text/70 mb-3 font-mono">{subtitle}</p>
      )}

      <div className="h-36 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={points}>
            <XAxis
              dataKey="label"
              tick={{ fontSize: 10, fill: "var(--text-primary)", opacity: 0.7 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis hide />
            <Tooltip
              contentStyle={{
                background: "var(--bg-secondary)",
                border: "2px solid var(--border-color)",
                borderRadius: "0px",
                boxShadow: "4px 4px 0px 0px rgba(0,0,0,1)",
                fontSize: "12px",
                color: "var(--text-primary)",
              }}
              formatter={(v: number | undefined) => [`${v ?? 0} ${unit}`, "Price"]}
              labelStyle={{ color: "var(--text-primary)" }}
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke={EMERALD}
              strokeWidth={2}
              dot={{ r: 3, fill: EMERALD, stroke: "#111827", strokeWidth: 2 }}
              activeDot={{ r: 5, fill: CYAN }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   SOIL COMPOSITION — Pie Chart
   card_type: "chart_pie"
   Expected data shape:
     data: { segments: [{name, value}] }
   ═══════════════════════════════════════════════════════════════════ */
interface SoilCompositionProps {
  title: string;
  subtitle?: string;
  data?: WidgetData;
}

export function SoilCompositionChart({
  title,
  subtitle,
  data,
}: SoilCompositionProps) {
  const segments: { name: string; value: number }[] = data?.segments ?? [
    { name: "Clay", value: 35 },
    { name: "Silt", value: 30 },
    { name: "Sand", value: 20 },
    { name: "Organic", value: 10 },
    { name: "Other", value: 5 },
  ];

  return (
    <div className="neo-box p-4 bg-surface">
      <p className="text-[11px] text-text/60 uppercase tracking-widest font-bold mb-0.5">
        {title}
      </p>
      {subtitle && (
        <p className="text-[10px] text-text/70 mb-3 font-mono">{subtitle}</p>
      )}

      <div className="h-36 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={segments}
              cx="50%"
              cy="50%"
              innerRadius={30}
              outerRadius={55}
              dataKey="value"
              stroke="none"
              paddingAngle={3}
            >
              {segments.map((_, idx) => (
                <Cell
                  key={idx}
                  fill={PIE_COLORS[idx % PIE_COLORS.length]}
                  opacity={0.85}
                />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                background: "var(--bg-secondary)",
                border: "2px solid var(--border-color)",
                borderRadius: "0px",
                boxShadow: "4px 4px 0px 0px rgba(0,0,0,1)",
                fontSize: "12px",
                color: "var(--text-primary)",
              }}
              formatter={(v: number | undefined, name: string | undefined) => [`${v ?? 0}%`, name ?? ""]}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-x-3 gap-y-1 mt-2">
        {segments.map((s, idx) => (
          <span key={s.name} className="flex items-center gap-1 text-[10px] text-text/70 font-mono">
            <span
              className="w-2 h-2 rounded-full inline-block"
              style={{ backgroundColor: PIE_COLORS[idx % PIE_COLORS.length] }}
            />
            {s.name}
          </span>
        ))}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   RECOMMENDATION LIST
   card_type: "list"
   Expected data shape:
     data: { items: [{name, confidence, season, reasoning?}] }
   ═══════════════════════════════════════════════════════════════════ */
interface RecommendationListProps {
  title: string;
  subtitle?: string;
  data?: WidgetData;
}

interface CropItem {
  name: string;
  confidence: number;
  season: string;
  reasoning?: string;
}

function confidenceColor(c: number): string {
  if (c >= 0.8) return "bg-emerald-100 text-emerald-800 border-emerald-800";
  if (c >= 0.5) return "bg-amber-100 text-amber-800 border-amber-800";
  return "bg-rose-100 text-rose-800 border-rose-800";
}

export function RecommendationList({
  title,
  subtitle,
  data,
}: RecommendationListProps) {
  const items: CropItem[] = data?.items ?? [
    { name: "Wheat (HD-2967)", confidence: 0.92, season: "Rabi" },
    { name: "Mustard", confidence: 0.78, season: "Rabi" },
    { name: "Chickpea", confidence: 0.65, season: "Rabi" },
  ];

  return (
    <div className="neo-box p-4 bg-surface">
      <p className="text-[11px] text-text/60 uppercase tracking-widest font-bold mb-0.5">
        {title}
      </p>
      {subtitle && (
        <p className="text-[10px] text-text/70 mb-3 font-mono">{subtitle}</p>
      )}

      <div className="space-y-2">
        {items.map((item) => (
          <div
            key={item.name}
            className="flex items-center justify-between bg-bg border-2 border-transparent hover:border-border hover:shadow-neo-sm transition-all rounded-sm px-3 py-2.5"
          >
            <div className="flex-1 min-w-0">
              <p className="text-sm font-bold text-text truncate">
                🌾 {item.name}
              </p>
              <p className="text-[10px] text-text/60 mt-0.5 font-mono">
                {item.season} season
                {item.reasoning && ` · ${item.reasoning}`}
              </p>
            </div>
            <span
              className={`text-[10px] font-bold px-2 py-0.5 border-2 shadow-sm ${confidenceColor(item.confidence)}`}
            >
              {Math.round(item.confidence * 100)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   CROP FACTORS — Bar Chart (N-P-K actual vs optimal)
   card_type: "chart_bar"
   Expected data shape:
     data: { factors: [{name, actual, optimal}] }
   ═══════════════════════════════════════════════════════════════════ */
interface CropFactorsProps {
  title: string;
  subtitle?: string;
  data?: WidgetData;
}

export function CropFactorsChart({
  title,
  subtitle,
  data,
}: CropFactorsProps) {
  const factors: { name: string; actual: number; optimal: number }[] =
    data?.factors ?? [
      { name: "Nitrogen", actual: 200, optimal: 80 },
      { name: "Phosphorus", actual: 42, optimal: 45 },
      { name: "Potassium", actual: 220, optimal: 40 },
    ];

  return (
    <div className="neo-box p-4 bg-surface">
      <p className="text-[11px] text-text/60 uppercase tracking-widest font-bold mb-0.5">
        {title}
      </p>
      {subtitle && (
        <p className="text-[10px] text-text/70 mb-3 font-mono">{subtitle}</p>
      )}

      <div className="h-40 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={factors}
            layout="vertical"
            margin={{ top: 4, right: 12, bottom: 4, left: 8 }}
          >
            <XAxis
              type="number"
              tick={{ fontSize: 10, fill: "var(--text-primary)", opacity: 0.7 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fontSize: 10, fill: "var(--text-primary)", opacity: 0.7 }}
              axisLine={false}
              tickLine={false}
              width={75}
            />
            <Tooltip
              contentStyle={{
                background: "var(--bg-secondary)",
                border: "2px solid var(--border-color)",
                borderRadius: "0px",
                boxShadow: "4px 4px 0px 0px rgba(0,0,0,1)",
                fontSize: "12px",
                color: "var(--text-primary)",
              }}
              formatter={(v: number | undefined, name: string | undefined) => [
                `${v ?? 0} kg/ha`,
                name === "actual" ? "Your Soil" : "Optimal",
              ]}
            />
            <Legend
              iconSize={8}
              wrapperStyle={{ fontSize: "10px", color: "var(--text-primary)" }}
              formatter={(value: string) =>
                value === "actual" ? "Your Soil" : "Optimal"
              }
            />
            <Bar
              dataKey="actual"
              fill={EMERALD}
              radius={[0, 4, 4, 0]}
              barSize={10}
              opacity={0.9}
            />
            <Bar
              dataKey="optimal"
              fill={AMBER}
              radius={[0, 4, 4, 0]}
              barSize={10}
              opacity={0.6}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Deficit / surplus indicators */}
      <div className="flex flex-wrap gap-x-3 gap-y-1 mt-2">
        {factors.map((f) => {
          const diff = f.actual - f.optimal;
          const pct = f.optimal > 0 ? Math.round((diff / f.optimal) * 100) : 0;
          const isDeficit = diff < 0;
          return (
            <span
              key={f.name}
              className={`text-[10px] font-medium ${
                isDeficit ? "text-rose-400" : "text-emerald-400"
              }`}
            >
              {f.name.slice(0, 1)}:{" "}
              {isDeficit ? `${pct}%` : `+${pct}%`}
            </span>
          );
        })}
      </div>
    </div>
  );
}
