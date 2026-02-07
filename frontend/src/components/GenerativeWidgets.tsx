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
  const points: { label: string; value: number }[] = data?.points ?? [
    { label: "Jan", value: 1200 },
    { label: "Feb", value: 1350 },
    { label: "Mar", value: 1100 },
    { label: "Apr", value: 980 },
    { label: "May", value: 1450 },
    { label: "Jun", value: 1600 },
  ];
  const unit: string = data?.unit ?? "₹/qtl";

  return (
    <div className="rounded-xl bg-gray-800/50 border border-white/[0.06] p-4">
      <p className="text-[11px] text-gray-400 uppercase tracking-wider font-medium mb-0.5">
        {title}
      </p>
      {subtitle && (
        <p className="text-[10px] text-gray-500 mb-3">{subtitle}</p>
      )}

      <div className="h-36 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={points}>
            <XAxis
              dataKey="label"
              tick={{ fontSize: 10, fill: "#6b7280" }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis hide />
            <Tooltip
              contentStyle={{
                background: "#1f2937",
                border: "1px solid #374151",
                borderRadius: "8px",
                fontSize: "12px",
                color: "#e5e7eb",
              }}
              formatter={(v: number | undefined) => [`${v ?? 0} ${unit}`, "Price"]}
              labelStyle={{ color: "#9ca3af" }}
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
    <div className="rounded-xl bg-gray-800/50 border border-white/[0.06] p-4">
      <p className="text-[11px] text-gray-400 uppercase tracking-wider font-medium mb-0.5">
        {title}
      </p>
      {subtitle && (
        <p className="text-[10px] text-gray-500 mb-3">{subtitle}</p>
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
                background: "#1f2937",
                border: "1px solid #374151",
                borderRadius: "8px",
                fontSize: "12px",
                color: "#e5e7eb",
              }}
              formatter={(v: number | undefined, name: string | undefined) => [`${v ?? 0}%`, name ?? ""]}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-x-3 gap-y-1 mt-2">
        {segments.map((s, idx) => (
          <span key={s.name} className="flex items-center gap-1 text-[10px] text-gray-400">
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
  if (c >= 0.8) return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
  if (c >= 0.5) return "bg-amber-500/20 text-amber-400 border-amber-500/30";
  return "bg-red-500/20 text-red-400 border-red-500/30";
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
    <div className="rounded-xl bg-gray-800/50 border border-white/[0.06] p-4">
      <p className="text-[11px] text-gray-400 uppercase tracking-wider font-medium mb-0.5">
        {title}
      </p>
      {subtitle && (
        <p className="text-[10px] text-gray-500 mb-3">{subtitle}</p>
      )}

      <div className="space-y-2">
        {items.map((item) => (
          <div
            key={item.name}
            className="flex items-center justify-between bg-gray-900/50 rounded-lg px-3 py-2.5 border border-white/[0.04] hover:border-white/[0.08] transition-colors"
          >
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-200 truncate">
                🌾 {item.name}
              </p>
              <p className="text-[10px] text-gray-500 mt-0.5">
                {item.season} season
                {item.reasoning && ` · ${item.reasoning}`}
              </p>
            </div>
            <span
              className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${confidenceColor(item.confidence)}`}
            >
              {Math.round(item.confidence * 100)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
