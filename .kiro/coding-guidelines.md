# Coding Guidelines: Orbital Nexus

## Core Principles

### 1. Simple, Readable, Demo-First

- Write code that works, not code that impresses
- Prioritize clarity over cleverness
- Avoid premature optimization
- Comment intent, not implementation
- Use descriptive variable and function names

**Good**:
```python
def calculate_crop_score(soil_type: str, humidity: float) -> float:
    """Calculate crop suitability score based on soil and humidity."""
    score = 0.0
    if soil_type == 'wet' and humidity > 60:
        score += 0.3  # Rice prefers wet soil with high humidity
    return score
```

**Bad**:
```python
def calc(s, h):
    # Calculate score
    return 0.3 if s == 'wet' and h > 60 else 0.0
```

### 2. No Premature Optimization

- Make it work first, optimize later (if time permits)
- Avoid complex algorithms when simple ones suffice
- Don't optimize for performance unless it's a bottleneck
- Profile before optimizing

**Good**: Linear regression for price prediction (simple, works)
**Bad**: LSTM neural network for price prediction (complex, overkill)

### 3. Clear Comments Explaining Intent

- Explain WHY, not WHAT
- Document business logic and domain knowledge
- Add comments for non-obvious decisions
- Use docstrings for all functions and classes

**Good**:
```python
# Use 3-year historical data to capture seasonal patterns
# while avoiding older data that may not reflect current market
historical_data = mandi_df[mandi_df['date'] >= three_years_ago]
```

**Bad**:
```python
# Filter data
historical_data = mandi_df[mandi_df['date'] >= three_years_ago]
```

### 4. Separate Concerns Strictly

- Frontend: UI components, user interactions, API calls
- Backend: API endpoints, requehandling
- AI Engine: Business logic, recommendations, predictions
- Data Layer: CSV loading, data fusion, filtering

**Do NOT**:
- Put business logic in frontend components
- Put UI logic in backend endpoints
- Mix data loading with AI algorithms

## Language-Specific Guidelines

### TypeScript (Frontend)

**File Naming**:
- Components: `PascalCase.tsx` (e.g., `PromptBox.tsx`)
- Utilities: `camelCase.ts` (e.g., `apiClient.ts`)
- Types: `types.ts` or `index.ts` in types folder

**Component Structure**:
```typescript
import React from 'react';

interface PromptBoxProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
}

export const PromptBox: React.FC<PromptBoxProps> = ({ onSubmit, isLoading }) => {
  const [query, setQuery] = React.useState('');

  const handleSubmit = () => {
    if (query.trim()) {
      onSubmit(query);
    }
  };

  return (
    <div className="prompt-box">
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask about crops, prices, or rotation plans..."
      />
      <button onClick={handleSubmit} disabled={isLoading}>
        {isLoading ? 'Processing...' : 'Submit'}
      </button>
    </div>
  );
};
```

**Type Definitions**:
```typescript
// Always define interfaces for props and data structures
interface AOI {
  lat: number;
  lng: number;
  district?: string;
  state?: string;
}

interface CropRecommendation {
  crop: string;
  score: number;
  reasons: string[];
  price_range: string;
  sustainability_note: string;
}
```

**Error Handling**:
```typescript
try {
  const response = await apiClient.postQuery(query, aoi);
  setData(response.data);
} catch (error) {
  if (error.response?.status === 404) {
    setError('No data available for this location');
  } else {
    setError('Something went wrong, please try again');
  }
  console.error('Query error:', error);
}
```

### Python (Backend)

**File Naming**:
- Modules: `snake_case.py` (e.g., `crop_recommender.py`)
- Classes: `PascalCase` (e.g., `CropRecommender`)
- Functions: `snake_case` (e.g., `calculate_score`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_LAT`)

**Class Structure**:
```python
from typing import List
import pandas as pd

class CropRecommender:
    """Recommends crops based on soil, weather, and market factors."""

    def __init__(self, fused_data: pd.DataFrame):
        """Initialize with fused dataset."""
        self.data = fused_data

    def recommend(self, aoi: dict, top_n: int = 3) -> List[dict]:
        """
        Generate crop recommendations for given AOI.

        Args:
            aoi: Area of interest with lat/lng
            top_n: Number of recommendations to return

        Returns:
            List of crop recommendations with scores and reasons
        """
        # Implementation
        pass
```

**Type Hints**:
```python
# Always use type hints for function parameters and return values
def calculate_price_trend(
    prices: pd.Series,
    years: int = 3
) -> tuple[float, float]:
    """Calculate price trend and percentage change."""
    # Implementation
    return trend, percentage_change
```

**Error Handling**:
```python
from fastapi import HTTPException

@app.post("/api/query")
async def process_query(request: QueryRequest):
    try:
        # Process query
        result = ai_engine.process(request.query, request.aoi)
        return {"success": True, "data": result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail="Data unavailable")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Allowed Libraries and Stack

### Frontend

**Required**:
- React 19: UI framework
- TypeScript: Type safety
- TailwindCSS: Styling
- Leaflet: Maps
- Recharts: Charts (fallback for Tembo SDK)
- Axios: HTTP client
- React Router: Routing

**Optional**:
- Framer Motion: Animations
- Tembo AI SDK: Generative UI (if available)
- Zustand: State management (if needed)

**Forbidden**:
- jQuery (use React)
- Bootstrap (use TailwindCSS)
- Moment.js (use native Date or date-fns)

### Backend

**Required**:
- FastAPI: Web framework
- Pydantic: Data validation
- Pandas: Data manipulation
- NumPy: Numerical operations
- Uvicorn: ASGI server

**Optional**:
- scikit-learn: Linear regression (if needed)
- python-dotenv: Environment variables

**Forbidden**:
- Django (too heavy for hackathon)
- Flask (FastAPI is better)
- SQLAlchemy (no database for MVP)

## Code Organization

### Frontend Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/          # Reusable components
│   │   │   ├── Button.tsx
│   │   │   └── Spinner.tsx
│   │   └── features/        # Feature-specific components
│   │       ├── PromptBox.tsx
│   │       ├── Map.tsx
│   │       └── Dashboard.tsx
│   ├── pages/
│   │   ├── LandingPage.tsx
│   │   └── SPAPage.tsx
│   ├── services/
│   │   └── apiClient.ts     # API calls
│   ├── hooks/
│   │   └── useLocation.ts   # Custom hooks
│   ├── types/
│   │   └── index.ts         # TypeScript types
│   ├── utils/
│   │   └── helpers.ts       # Utility functions
│   ├── App.tsx
│   └── main.tsx
├── public/
├── package.json
└── vite.config.ts
```

### Backend Structure

```
backend/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       └── query.py     # API endpoints
│   ├── core/
│   │   └── config.py        # Configuration
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   ├── services/
│   │   ├── crop_recommender.py
│   │   ├── price_predictor.py
│   │   └── rotation_planner.py
│   ├── data/
│   │   └── data_loader.py   # CSV loading
│   └── main.py              # FastAPI app
├── data/                    # CSV files
├── requirements.txt
└── .env
```

## Testing Guidelines

### Property-Based Tests

**Frontend (fast-check)**:
```typescript
import fc from 'fast-check';

// Feature: orbital-nexus-mvp, Property 3: Query Suggestion Presence
test('prompt box always shows 3 suggestions', () => {
  fc.assert(
    fc.property(fc.boolean(), (isVisible) => {
      if (isVisible) {
        const suggestions = getQuerySuggestions();
        expect(suggestions).toHaveLength(3);
      }
    })
  );
});
```

**Backend (Hypothesis)**:
```python
from hypothesis import given, strategies as st

# Feature: orbital-nexus-mvp, Property 8: Top-N Recommendation Constraint
@given(st.text(min_size=1, max_size=500))
def test_recommendations_return_top_3(query):
    """For any query, system returns exactly 3 recommendations."""
    result = recommender.recommend(query, aoi=default_aoi)
    assert len(result) == 3
    assert all(0 <= r['score'] <= 1 for r in result)
```

### Unit Tests

**Frontend (Jest + React Testing Library)**:
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { PromptBox } from './PromptBox';

test('submits query on button click', () => {
  const onSubmit = jest.fn();
  render(<PromptBox onSubmit={onSubmit} isLoading={false} />);

  const input = screen.getByPlaceholderText(/ask about crops/i);
  fireEvent.change(input, { target: { value: 'Best crop?' } });

  const button = screen.getByText(/submit/i);
  fireEvent.click(button);

  expect(onSubmit).toHaveBeenCalledWith('Best crop?');
});
```

**Backend (Pytest)**:
```python
def test_query_endpoint_returns_recommendations(client):
    """Test POST /api/query returns valid recommendations."""
    response = client.post(
        "/api/query",
        json={"query": "Best crop?", "aoi": {"lat": 28.4744, "lng": 77.5040}}
    )
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert len(data['data']['recommendations']) == 3
```

## Git Workflow

### Commit Messages

**Format**: `<type>: <description>`

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring
- `test`: Add tests
- `docs`: Documentation
- `style`: Formatting

**Examples**:
- `feat: add crop recommendation endpoint`
- `fix: handle empty query gracefully`
- `refactor: extract data fusion logic`
- `test: add property tests for recommendations`

### Branch Strategy

**Hackathon (Simple)**:
- `main`: Production-ready code
- Feature branches: `feature/prompt-box`, `feature/map-component`
- Merge to main after testing

### Pull Requests

- Keep PRs small and focused
- Test before merging
- Review by at least one team member
- Delete branch after merge

## Performance Guidelines

### Frontend

- Lazy load routes and components
- Debounce user input (query suggestions)
- Memoize expensive calculations (React.useMemo)
- Optimize images (compress, use WebP)
- Code splitting (React.lazy)

### Backend

- Cache fused data for default location
- Use Pandas efficiently (vectorized operations)
- Avoid loops when possible
- Profile slow endpoints (cProfile)

## Accessibility Guidelines

- Use semantic HTML (header, nav, main, footer)
- Add ARIA labels to interactive elements
- Ensure keyboard navigation works
- Maintain color contrast (4.5:1 minimum)
- Add alt text to images and visualizations

## Security Guidelines

- Validate all user input (query length, coordinates)
- Sanitize input to prevent injection attacks
- Use HTTPS in production
- Don't commit secrets (.env in .gitignore)
- Set CORS to specific origins (not *)

## Documentation Guidelines

- README with setup instructions
- API documentation (FastAPI auto-generates)
- Code comments for complex logic
- Docstrings for all functions and classes
- No time for extensive documentation (hackathon)

## Definition of Done

A task is complete when:
1. Code works as specified
2. Tests pass (property tests and unit tests)
3. Code is readable and commented
4. No console errors or warnings
5. Committed to Git with clear message
6. Reviewed by team member (if time permits)
