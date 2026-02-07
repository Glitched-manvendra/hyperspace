import { ArrowLeft, Satellite } from "lucide-react";

interface HeaderProps {
  onBack?: () => void;
}

/**
 * Header — Orbital Nexus branding bar (Space-Glass aesthetic)
 */
function Header({ onBack }: HeaderProps) {
  return (
    <header className="flex items-center justify-between px-6 py-3 glass-panel border-b border-glass-border">
      {/* Logo + title */}
      <div className="flex items-center gap-3">
        {onBack && (
          <button
            onClick={onBack}
            className="text-sage hover:text-white mr-1 transition-colors"
            title="Back to Landing"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
        )}
        <div className="w-8 h-8 rounded-lg overflow-hidden">
          <img src="/logo.png" alt="Orbital Nexus" className="w-full h-full object-cover" />
        </div>
        <div>
          <h1 className="text-base font-display font-bold text-white tracking-tight">
            Orbital Nexus
          </h1>
          <p className="text-[10px] text-sage uppercase tracking-widest">
            Multi-Satellite Data Fusion Dashboard
          </p>
        </div>
      </div>

      {/* Status indicator */}
      <div className="flex items-center gap-2 glass-card rounded-full px-3 py-1.5">
        <Satellite className="w-3.5 h-3.5 text-primary" />
        <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
        <span className="text-xs text-sage">Live</span>
      </div>
    </header>
  );
}

export default Header;
