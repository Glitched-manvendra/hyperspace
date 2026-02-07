# Backend — Orbital Nexus

FastAPI backend for multi-satellite data fusion and AI-driven query processing.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Endpoints

| Method | Path    | Description                    |
| ------ | ------- | ------------------------------ |
| GET    | /health | Health check                   |
| POST   | /query  | Process natural language query |

## Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI entrypoint
│   ├── api/
│   │   └── routes.py    # API route definitions
│   ├── services/
│   │   └── fusion.py    # Data fusion logic
│   ├── ai/
│   │   └── intent.py    # Query intent parsing
│   ├── models/
│   │   └── schemas.py   # Pydantic models
│   └── utils/
│       └── data_loader.py  # CSV/JSON loading helpers
└── requirements.txt
```
