import { motion } from "framer-motion";
import type { QueryResponse, UIInstruction } from "../utils/api";
import DashboardCard from "./DashboardCard";
import {
  PriceTrendChart,
  SoilCompositionChart,
  RecommendationList,
  CropFactorsChart,
} from "./GenerativeWidgets";

interface SidebarProps {
  response: QueryResponse | null;
  loading: boolean;
  width?: number;
}

/**
 * WidgetFactory — Server-Driven UI renderer
 *
 * Maps backend card_type to the correct React component.
 * Supports: chart_line, chart_pie, list, and stat (default).
 */
function WidgetFactory({ card }: { card: UIInstruction }) {
  switch (card.card_type) {
    case "chart_line":
      return (
        <PriceTrendChart
          title={card.title}
          subtitle={card.subtitle}
          data={card.data}
        />
      );
    case "chart_pie":
      return (
        <SoilCompositionChart
          title={card.title}
          subtitle={card.subtitle}
          data={card.data}
        />
      );
    case "chart_bar":
      return (
        <CropFactorsChart
          title={card.title}
          subtitle={card.subtitle}
          data={card.data}
        />
      );
    case "list":
      return (
        <RecommendationList
          title={card.title}
          subtitle={card.subtitle}
          data={card.data}
        />
      );
    default:
      return (
        <DashboardCard
          cardType={card.card_type}
          title={card.title}
          value={card.value}
          subtitle={card.subtitle}
          color={card.color}
        />
      );
  }
}

/**
 * Sidebar — scrollable panel of generative dashboard widgets (Space-Glass)
 *
 * Shows placeholder cards when idle, server-driven widgets after a query.
 */
function Sidebar({ response, loading, width = 320 }: SidebarProps) {
  const placeholderCards: UIInstruction[] = [
    { card_type: "stat", title: "Temperature", value: "--", subtitle: "Awaiting query", color: "gray" },
    { card_type: "stat", title: "Rainfall", value: "--", subtitle: "Awaiting query", color: "gray" },
    { card_type: "stat", title: "Soil Moisture", value: "--", subtitle: "Awaiting query", color: "gray" },
    { card_type: "stat", title: "NDVI", value: "--", subtitle: "Awaiting query", color: "gray" },
  ];

  const cards = response?.ui_instructions ?? placeholderCards;

  return (
    <aside
      className="bg-surface border-r-2 border-border flex flex-col z-20 shadow-neo"
      style={{ width: `${width}px`, minWidth: `${width}px` }}
    >
      {/* Section title */}
      <div className="px-4 py-3 border-b-2 border-border">
        <h2 className="text-xs font-display font-bold text-text/70 uppercase tracking-widest">
          Dashboard
        </h2>
        {response && (
          <p className="text-[10px] text-primary mt-1">
            {response.fused_data.data_sources.join(" · ")}
          </p>
        )}
      </div>

      {/* Scrollable widgets */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-3">
        {loading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <div
              key={i}
              className="h-24 bg-black/5 dark:bg-white/5 border-2 border-dashed border-text/20 rounded-none animate-pulse"
            />
          ))
        ) : (
          cards.map((card, i) => (
            <motion.div
              key={`${card.card_type}-${card.title}-${i}`}
              initial={{ opacity: 0, x: -24 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1, duration: 0.4, ease: "easeOut" }}
            >
              <WidgetFactory card={card} />
            </motion.div>
          ))
        )}
      </div>
    </aside>
  );
}

export default Sidebar;
