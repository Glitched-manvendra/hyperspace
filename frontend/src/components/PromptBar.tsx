import { useState, type FormEvent } from "react";
import { Send, Loader2 } from "lucide-react";

interface PromptBarProps {
  onSubmit: (query: string) => void;
  loading: boolean;
}

/**
 * PromptBar — ChatGPT-style input at the bottom (Space-Glass)
 *
 * User types natural language queries about satellite data.
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
    <div className="bg-surface border-t-2 border-border z-20 shadow-neo">
      {/* Progress bar */}
      {loading && (
        <div className="h-0.5 bg-white/5">
          <div className="h-full bg-gradient-to-r from-primary to-accent animate-[progress_1.5s_ease-in-out_infinite] w-1/3 rounded-full" />
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex items-center gap-3 px-6 py-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about satellite data... (e.g., 'Crops for Sultanpur' or 'NDVI for Agra and Mathura')"
          className="flex-1 neo-input"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="neo-button bg-primary text-black font-bold px-6 py-3 text-sm disabled:opacity-50 disabled:shadow-none flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Analyzing…
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              Send
            </>
          )}
        </button>
      </form>
    </div>
  );
}

export default PromptBar;
