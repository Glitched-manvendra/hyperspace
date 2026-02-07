interface DashboardCardProps {
  cardType: string;
  title: string;
  value: string;
  subtitle: string;
  color: string;
}

/** Color map for card accent borders and icons */
const colorMap: Record<string, string> = {
  blue: "border-blue-500 text-blue-400",
  orange: "border-orange-500 text-orange-400",
  green: "border-green-500 text-green-400",
  emerald: "border-emerald-500 text-emerald-400",
  yellow: "border-yellow-500 text-yellow-400",
  red: "border-red-500 text-red-400",
  gray: "border-gray-600 text-gray-500",
};

/** Icon map by card type */
const iconMap: Record<string, string> = {
  stat: "📊",
  chart: "📈",
  alert: "⚠️",
  recommendation: "🌾",
};

/**
 * DashboardCard — single data card in the sidebar
 *
 * Rendered dynamically based on UIInstruction from the backend.
 * The Tembo SDK would replace these with richer generative components.
 */
function DashboardCard({ cardType, title, value, subtitle, color }: DashboardCardProps) {
  const colorClasses = colorMap[color] ?? colorMap.blue;
  const icon = iconMap[cardType] ?? "📋";

  return (
    <div
      className={`bg-gray-800/60 rounded-lg border-l-4 p-4 hover:bg-gray-800 transition-colors ${colorClasses}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-[11px] text-gray-400 uppercase tracking-wider font-medium">
            {title}
          </p>
          <p className={`text-2xl font-bold mt-1 ${colorClasses.split(" ")[1]}`}>
            {value}
          </p>
          {subtitle && (
            <p className="text-[11px] text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
        <span className="text-lg">{icon}</span>
      </div>
    </div>
  );
}

export default DashboardCard;
