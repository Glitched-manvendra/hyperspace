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
function Sidebar({ response, loading }: SidebarProps) {
  const placeholderCards: UIInstruction[] = [
    { card_type: "stat", title: "Temperature", value: "--", subtitle: "Awaiting query", color: "gray" },
    { card_type: "stat", title: "Rainfall", value: "--", subtitle: "Awaiting query", color: "gray" },
    { card_type: "stat", title: "Soil Moisture", value: "--", subtitle: "Awaiting query", color: "gray" },
    { card_type: "stat", title: "NDVI", value: "--", subtitle: "Awaiting query", color: "gray" },
  ];

  const cards = response?.ui_instructions ?? placeholderCards;

  return (
    <aside className="w-80 glass-panel border-r border-glass-border flex flex-col">
      {/* Section title */}
      <div className="px-4 py-3 border-b border-glass-border">
        <h2 className="text-xs font-display font-semibold text-sage uppercase tracking-wider">
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
              className="h-24 bg-white/5 rounded-xl animate-pulse"
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
