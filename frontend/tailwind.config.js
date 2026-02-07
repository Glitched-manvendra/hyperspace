/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class", // Enable class-based dark mode
  theme: {
    extend: {
      colors: {
        // Neo-Brutalism Palette
        bg: "var(--bg-primary)",
        surface: "var(--bg-secondary)",
        text: "var(--text-primary)",
        border: "var(--border-color)",

        // Brand Colors
        primary: "#88cc00", // Acid Green
        secondary: "#ff00ff", // Magenta
        accent: "#06b6d4", // Cyan

        // Legacy aliases (mapped to new system where possible or kept for compatibility)
        "glass-border": "rgba(255, 255, 255, 0.08)",
        nexus: {
          dark: "#0a0e1a",
          panel: "#111827",
          accent: "#3b82f6",
          glow: "#60a5fa",
        },
      },
      boxShadow: {
        neo: "4px 4px 0px 0px rgba(0,0,0,1)",
        "neo-sm": "2px 2px 0px 0px rgba(0,0,0,1)",
        "neo-lg": "8px 8px 0px 0px rgba(0,0,0,1)",
      },
      fontFamily: {
        sans: ["Outfit", "Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
        display: ["Space Grotesk", "Outfit", "sans-serif"],
      },
      backgroundImage: {
        "space-gradient": "radial-gradient(circle at center, var(--bg-secondary) 0%, var(--bg-primary) 100%)",
      },
    },
  },
  plugins: [],
};
