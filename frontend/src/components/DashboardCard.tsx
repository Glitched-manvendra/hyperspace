interface DashboardCardProps {
  cardType: string;
  title: string;
  value: string;
  subtitle: string;
  color: string;
}

/** Color map for card accent borders and icons (Space-Glass) */
const colorMap: Record<string, { border: string; text: string; glow: string }> = {
  blue:    { border: "border-blue-500/40",    text: "text-blue-400",    glow: "shadow-blue-500/10" },
  orange:  { border: "border-orange-500/40",  text: "text-orange-400",  glow: "shadow-orange-500/10" },
  green:   { border: "border-primary/40",     text: "text-primary",     glow: "shadow-primary/10" },
  emerald: { border: "border-primary/40",     text: "text-primary",     glow: "shadow-primary/10" },
  yellow:  { border: "border-gold/40",        text: "text-gold",        glow: "shadow-gold/10" },
  red:     { border: "border-red-500/40",     text: "text-red-400",     glow: "shadow-red-500/10" },
  gray:    { border: "border-white/10",       text: "text-sage",        glow: "" },
};

/** Icon map by card type */
const iconMap: Record<string, string> = {
  stat: "📊",
  chart: "📈",
  alert: "⚠️",
  recommendation: "🌾",
};

/**
 * DashboardCard — single stat card in the sidebar (Space-Glass)
 *
 * Rendered dynamically via UIInstruction from the backend.
 */
function DashboardCard({ cardType, title, value, subtitle, color }: DashboardCardProps) {
  const scheme = colorMap[color] ?? colorMap.blue;
  const icon = iconMap[cardType] ?? "📋";

  return (
    <div
      className={`glass-card rounded-xl border-l-4 p-4 hover:bg-white/[0.06] transition-colors ${scheme.border} ${scheme.glow}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-[11px] text-sage uppercase tracking-wider font-medium">
            {title}
          </p>
          <p className={`text-2xl font-display font-bold mt-1 ${scheme.text}`}>
            {value}
          </p>
          {subtitle && (
            <p className="text-[11px] text-sage/70 mt-1">{subtitle}</p>
          )}
        </div>
        <span className="text-lg">{icon}</span>
      </div>
    </div>
  );
}

export default DashboardCard;
