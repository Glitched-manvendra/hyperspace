import AnimatedIcon from "./AnimatedIcon";

interface DashboardCardProps {
  cardType: string;
  title: string;
  value: string;
  subtitle: string;
  color: string;
}

/** Color map for card accents (Neo-Brutalist) */
const colorMap: Record<string, { border: string; text: string; bg: string }> = {
  blue: { border: "border-blue-500", text: "text-blue-600 dark:text-blue-400", bg: "bg-blue-50 dark:bg-blue-900/20" },
  orange: { border: "border-orange-500", text: "text-orange-600 dark:text-orange-400", bg: "bg-orange-50 dark:bg-orange-900/20" },
  green: { border: "border-primary", text: "text-emerald-700 dark:text-emerald-400", bg: "bg-emerald-50 dark:bg-emerald-900/20" },
  emerald: { border: "border-primary", text: "text-emerald-700 dark:text-emerald-400", bg: "bg-emerald-50 dark:bg-emerald-900/20" },
  yellow: { border: "border-yellow-500", text: "text-yellow-700 dark:text-yellow-400", bg: "bg-yellow-50 dark:bg-yellow-900/20" },
  red: { border: "border-red-500", text: "text-red-700 dark:text-red-400", bg: "bg-red-50 dark:bg-red-900/20" },
  gray: { border: "border-text", text: "text-text", bg: "bg-surface" },
};

/**
 * DashboardCard — single stat card in the sidebar (Neo-Brutalist)
 *
 * Rendered dynamically via UIInstruction from the backend.
 */
function DashboardCard({ cardType: _cardType, title, value, subtitle, color }: DashboardCardProps) {
  const scheme = colorMap[color] ?? colorMap.gray;

  return (
    <div
      className={`neo-box p-4 hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-neo-sm transition-all ${scheme.bg} ${scheme.border}`}
    >
      <div className="flex items-start gap-4">
        <div className="text-xl filter drop-shadow-sm mt-0.5">
          <AnimatedIcon type={title} />
        </div>
        <div className="flex-1">
          <p className="text-[11px] text-text/60 uppercase tracking-widest font-bold">
            {title}
          </p>
          <p className="text-2xl font-display font-bold mt-1 text-text">
            {value}
          </p>
          {subtitle && (
            <p className="text-[11px] text-text/70 mt-1 font-mono">{subtitle}</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default DashboardCard;
