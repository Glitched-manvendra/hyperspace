interface HeaderProps {
  onBack?: () => void;
}

/**
 * Header — Orbital Nexus branding bar
 */
function Header({ onBack }: HeaderProps) {
  return (
    <header className="flex items-center justify-between px-6 py-3 bg-nexus-panel border-b border-gray-800">
      {/* Logo + title */}
      <div className="flex items-center gap-3">
        {onBack && (
          <button
            onClick={onBack}
            className="text-gray-400 hover:text-white mr-1 transition-colors"
            title="Back to Landing"
          >
            ←
          </button>
        )}
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-cyan-400 flex items-center justify-center">
          <span className="text-sm font-bold">🛰️</span>
        </div>
        <div>
          <h1 className="text-lg font-semibold text-white tracking-tight">
            Orbital Nexus
          </h1>
          <p className="text-[10px] text-gray-500 uppercase tracking-widest">
            Multi-Satellite Data Fusion Dashboard
          </p>
        </div>
      </div>

      {/* Status indicator */}
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
        <span className="text-xs text-gray-400">Offline Mode</span>
      </div>
    </header>
  );
}

export default Header;
