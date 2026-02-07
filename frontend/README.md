# Frontend — Orbital Nexus

React 19 + TypeScript + TailwindCSS + Leaflet SPA for multi-satellite data visualization.

## Setup

```bash
npm install
npm run dev
```

Opens at [http://localhost:5173](http://localhost:5173).

## Layout

- **Header**: Branding + offline status indicator
- **Sidebar**: Generative dashboard cards (driven by backend UI instructions)
- **Map**: Leaflet map centered on Greater Noida
- **Prompt Bar**: Natural language input (ChatGPT-style)

## Key Files

- `src/App.tsx` — Main layout and state management
- `src/components/MapView.tsx` — Leaflet map component
- `src/components/Sidebar.tsx` — Dashboard card panel
- `src/components/PromptBar.tsx` — Query input
- `src/utils/api.ts` — Backend API client
