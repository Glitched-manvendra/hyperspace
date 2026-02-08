import { Satellite, LogOut, User } from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";

interface HeaderProps {
  onBack?: () => void;
  user?: { phone: string; name: string; village: string } | null;
  onLogout?: () => void;
}

/**
 * Header — Orbital Nexus branding bar (Space-Glass aesthetic)
 */
function Header({ onBack, user, onLogout }: HeaderProps) {
  return (
    <header className="flex items-center justify-between px-6 py-3 bg-surface border-b-2 border-border">
      {/* Logo + title */}
      <button
        onClick={onBack}
        className="group flex items-center gap-3 hover:opacity-80 transition-all text-left"
        title="Go to Home"
      >
        <ThemeToggle />
        <div className="w-10 h-10 border-2 border-border shadow-neo-sm overflow-hidden bg-white group-hover:border-primary transition-colors">
          <img
            src="/logo.png"
            alt="Orbital Nexus"
            className="w-full h-full object-contain p-1"
          />
        </div>
        <div>
          <h1 className="text-lg font-display font-bold text-text tracking-tight leading-none group-hover:text-primary transition-colors">
            Orbital Nexus
          </h1>
          <p className="text-[10px] text-text/70 uppercase tracking-widest font-mono">
            Multi-Satellite Data Fusion Dashboard
          </p>
        </div>
      </button>

      {/* Right side: user + status */}
      <div className="flex items-center gap-3">
        {/* User chip */}
        {user && user.phone !== "demo" && (
          <div className="flex items-center gap-2 neo-box px-3 py-1.5 bg-surface">
            <User className="w-3.5 h-3.5 text-text" />
            <span className="text-xs text-text font-bold max-w-[120px] truncate">
              {user.name}
            </span>
            {onLogout && (
              <button
                onClick={onLogout}
                className="text-text/60 hover:text-red-500 transition-colors ml-1"
                title="Sign out"
              >
                <LogOut className="w-3 h-3" />
              </button>
            )}
          </div>
        )}

        {/* Status indicator */}
        <div className="flex items-center gap-2 neo-box px-3 py-1.5 bg-surface">
          <Satellite className="w-3.5 h-3.5 text-primary" />
          <div className="w-2 h-2 rounded-full bg-primary animate-pulse border border-black" />
          <span className="text-xs text-text font-bold">Live</span>
        </div>
      </div>
    </header>
  );
}

export default Header;
