import { motion } from "framer-motion";
import type { QueryResponse } from "../utils/api";
import DashboardCard from "./DashboardCard";

interface SidebarProps {
  response: QueryResponse | null;
  loading: boolean;
}

/**
 * Sidebar — scrollable panel of dashboard cards
 *
 * Shows placeholder cards when idle, data-driven cards after a query.
 */
function Sidebar({ response, loading }: SidebarProps) {
  // Placeholder cards shown before any query
  const placeholderCards = [
    { card_type: "stat", title: "Temperature", value: "--", subtitle: "Awaiting query", color: "gray" },
    { card_type: "stat", title: "Rainfall", value: "--", subtitle: "Awaiting query", color: "gray" },
    { card_type: "stat", title: "Soil Moisture", value: "--", subtitle: "Awaiting query", color: "gray" },
    { card_type: "stat", title: "NDVI", value: "--", subtitle: "Awaiting query", color: "gray" },
  ];

  const cards = response?.ui_instructions ?? placeholderCards;

  return (
    <aside className="w-72 bg-nexus-panel border-r border-gray-800 flex flex-col">
      {/* Section title */}
      <div className="px-4 py-3 border-b border-gray-800">
        <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
          Dashboard
        </h2>
        {response && (
          <p className="text-[10px] text-nexus-glow mt-1">
            {response.fused_data.data_sources.join(" · ")}
          </p>
        )}
      </div>

      {/* Scrollable cards */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-3">
        {loading ? (
          // Loading skeleton
          Array.from({ length: 4 }).map((_, i) => (
            <div
              key={i}
              className="h-24 bg-gray-800 rounded-lg animate-pulse"
            />
          ))
        ) : (
          cards.map((card, i) => (
            <motion.div
              key={`${card.title}-${i}`}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
            >
              <DashboardCard
                cardType={card.card_type}
                title={card.title}
                value={card.value}
                subtitle={card.subtitle}
                color={card.color}
              />
            </motion.div>
          ))
        )}
      </div>
    </aside>
  );
}

export default Sidebar;
