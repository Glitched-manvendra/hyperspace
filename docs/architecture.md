# Architecture — Orbital Nexus

## High-Level Flow

```
User Query (natural language)
        │
        ▼
┌──────────────────┐
│   React Frontend │  ← Prompt input, map, dashboard
│   (SPA + Leaflet)│
└────────┬─────────┘
         │  POST /query
         ▼
┌──────────────────┐
│  FastAPI Backend  │  ← Intent parsing, data fusion, AI logic
│  (Python 3.12)   │
└────────┬─────────┘
         │  Reads from
         ▼
┌──────────────────┐
│  Offline Datasets │  ← CSV/JSON (weather, soil, NDVI, crop)
│  (data/ folder)   │
└──────────────────┘
```

## Data Flow

1. User types a query: _"What crop should I grow in Greater Noida this season?"_
2. Frontend sends `POST /query` with `{ query, lat, lon }`
3. Backend:
   - Parses intent (crop recommendation, weather analysis, soil check, etc.)
   - Loads relevant fused datasets
   - Generates structured response + UI instructions
4. Frontend:
   - Renders guidance text
   - Generates dashboard cards via Tembo SDK
   - Updates map markers/layers

## Key Design Decisions

- **Offline-first**: Zero external API calls — all data bundled locally
- **Fusion, not aggregation**: Cross-correlating multiple satellite data sources
- **Generative UI**: Dashboard cards are dynamically composed per query
- **Single-page app**: No routing — everything on one screen for demo clarity
