/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Space-Agri Palette
        background: "#0a0e1a",
        surface: "#111827",
        primary: "#10b981",
        accent: "#06b6d4",
        gold: "#f59e0b",
        sage: "#9ca3af",
        // Glass specific
        glass: "rgba(17, 24, 39, 0.7)",
        "glass-border": "rgba(255, 255, 255, 0.08)",
        // Legacy aliases
        nexus: {
          dark: "#0a0e1a",
          panel: "#111827",
          accent: "#3b82f6",
          glow: "#60a5fa",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
        display: ["Space Grotesk", "Inter", "sans-serif"],
      },
      backgroundImage: {
        "space-gradient": "radial-gradient(circle at center, #1e293b 0%, #0a0e1a 100%)",
        "glow-green": "conic-gradient(from 180deg at 50% 50%, #10b981 0deg, #06b6d4 180deg, #10b981 360deg)",
      },
      animation: {
        "spin-slow": "spin 12s linear infinite",
        "pulse-glow": "pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
      keyframes: {
        "pulse-glow": {
          "0%, 100%": { opacity: "1", boxShadow: "0 0 20px rgba(16, 185, 129, 0.2)" },
          "50%": { opacity: ".7", boxShadow: "0 0 10px rgba(16, 185, 129, 0.1)" },
        },
      },
    },
  },
  plugins: [],
};
