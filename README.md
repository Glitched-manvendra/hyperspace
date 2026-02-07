# Orbital Nexus — Multi-Satellite Data Fusion Dashboard

> **Hyperspace Innovation Hackathon 2026 — Problem Statement #4**

## What It Does

Orbital Nexus fuses multi-satellite data (weather, soil, NDVI, crop patterns) into a single, AI-driven dashboard that lets farmers, researchers, and policymakers ask natural-language questions and get actionable, location-specific insights — completely offline.

## Stack

| Layer    | Tech                                        |
| -------- | ------------------------------------------- |
| Frontend | React 19, TypeScript, TailwindCSS, Leaflet  |
| Backend  | Python 3.12, FastAPI                        |
| AI/UI    | Tembo AI SDK (generative dashboards)        |
| Data     | Offline CSV/JSON (Kaggle + public datasets) |

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) — backend runs at [http://localhost:8000](http://localhost:8000).

## Project Structure

```
orbital-nexus/
├── backend/        # FastAPI backend + AI logic
├── frontend/       # React SPA + map + dashboard
├── data/           # Offline datasets (raw + processed)
├── scripts/        # Data preprocessing & fusion helpers
├── docs/           # Architecture, demo script, dataset docs
├── deployment/     # Deployment notes (Vercel, Hostinger)
└── README.md       # You are here
```

## Team

Orbital Nexus — Hyperspace 2026

## License

MIT
