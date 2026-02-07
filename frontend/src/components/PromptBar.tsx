import { useState, type FormEvent } from "react";

interface PromptBarProps {
  onSubmit: (query: string) => void;
  loading: boolean;
}

/**
 * PromptBar — ChatGPT-style input at the bottom of the screen
 *
 * User types natural language queries about satellite data.
 * Includes a progress indicator when waiting for backend response.
 */
function PromptBar({ onSubmit, loading }: PromptBarProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || loading) return;
    onSubmit(trimmed);
    setQuery("");
  };

  return (
    <div className="border-t border-gray-800 bg-nexus-panel">
      {/* Progress bar */}
      {loading && (
        <div className="h-0.5 bg-gray-800">
          <div className="h-full bg-nexus-accent animate-[progress_1.5s_ease-in-out_infinite] w-1/3 rounded-full" />
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex items-center gap-3 px-6 py-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about satellite data... (e.g., 'What crop should I grow in Greater Noida?')"
          className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-nexus-accent focus:ring-1 focus:ring-nexus-accent transition-colors"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="bg-nexus-accent hover:bg-blue-600 disabled:bg-gray-700 disabled:text-gray-500 text-white font-medium px-6 py-3 rounded-lg text-sm transition-colors"
        >
          {loading ? "Analyzing..." : "Send"}
        </button>
      </form>
    </div>
  );
}

export default PromptBar;
