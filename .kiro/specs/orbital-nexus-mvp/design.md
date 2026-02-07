# Design Document: Orbital Nexus MVP

## Overview

Orbital Nexus is a web-based micro-SaaS platform that provides AI-driven crop recommendations and price predictions for Indian farmers by fusing multi-source public datasets. The system consists of a React-based single-page application (SPA) with a scrollable landing page, a FastAPI backend for data processing, and an offline CSV-based data layer.

The architecture prioritizes demo stability, visual impact, and rapid development within a 36-hour hackathon timeline. The system uses rule-based AI for crop recommendations, simple linear regression for price predictions, and generative UI components for dynamic dashboard rendering.

Key design principles:
- Offline-first: All data pre-loaded, no external API dependencies
- Demo-ready: Pre-computed results for default location (Greater Noida)
- Visual impact: Maps, graphs, charts for judge appeal
- Ethical: Public data only, guidance language (not predictions)
- Modular: Separate frontend, backend, data, and AI layers

## Architecture

### High-Level Architecture

```
User Browser
    |
    v
[Landing Page] --"Get Started"--> [SPA]
    |                                |
    |                                v
    |                    +------------------------+
    |                    |   React Frontend       |
    |                    |  - Prompt Box          |
    |                    |  - Map (Leaflet)       |
    |                    |  - Dashboard Sidebar   |
    |                    +------------------------+
    |                                |
    |                                v (HTTP/REST)
    |                    +------------------------+
    |                    |   FastAPI Backend      |
    |                    |  - Query Parser        |
    |                    |  - AI Engine           |
    |                    |  - Data Fusion Layer   |
    |                    +------------------------+
    |                                |
    |                                v
    |                    +------------------------+
    |                    |   Data Layer           |
    |                    |  - CSV Files (Pandas)  |
    |                    |  - Satellite (NDVI)    |
    |                    |  - Soil/Weather        |
    |                    |  - Mandi Prices        |
    |                    +------------------------+
```

### Component Layers

1. **Presentation Layer (Frontend)**
   - Landing Page: Scrollable marketing page with hero, problem, solution, business model, impact sections
   - SPA: Full-screen application with prompt box, map, and dashboard
   - Technologies: React 19, TypeScript, TailwindCSS, Leaflet, Recharts, Framer Motion

2. **API Layer (Backend)**
   - FastAPI endpoints for query processing
   - Query parser to identify intent (crop recommendation, price prediction, rotation planning)
   - Response formatter for dashboard generation
   - Technologies: Python 3.12, FastAPI, Pydantic

3. **Business Logic Layer (AI Engine)**
   - Rule-based crop recommendation system
   - Linear regression price prediction
   - Rotation plan generator
   - Technologies: NumPy, Pandas, scikit-learn (optional)

4. **Data Layer**
   - Offline CSV storage in /data folder
   - Pandas-based data fusion and querying
   - Location-based filtering (lat/long matching)
   - Datasets: Landsat/Sentinel (NDVI), Kaggle soil/weather CSVs, mandi price CSVs

### Data Flow

1. User enters query in prompt box → Frontend sends POST request to /api/query
2. Backend parses query intent (crop/price/rotation)
3. Backend queries Fused_Data filtered by user's AOI
4. AI Engine applies rules/calculations to generate recommendations
5. Backend formats response with dashboard components (graphs, charts, lists)
6. Frontend renders dashboard in sidebar and updates map overlays
7. Total flow time: <5 seconds

## Components and Interfaces

### Frontend Components

#### 1. Landing Page Component
- **Purpose**: Marketing page to pitch micro-SaaS concept
- **Sections**:
  - Hero: Logo, tagline ("Guided Farming with Satellite Intelligence"), CTA button
  - Problem: Infographic showing supply-demand imbalances (potato glut example)
  - Solution: Feature showcase with screenshots
  - Business: Freemium model table (free vs. premium)
  - Impact: Sustainability stats (e.g., "20-30% yield improvement")
  - Footer: Team info, social handles (@OrbitalNexusIN), data attributions
- **Navigation**: "Get Started" button routes to /app (SPA)

#### 2. SPA Layout Component
- **Structure**:
  - Top: Logo and location indicator
  - Center-right: Leaflet map (60% width)
  - Left: Dashboard sidebar (40% width, scrollable)
  - Bottom-center: Prompt box (fixed position, overlays map)
- **Responsive**: Mobile-first, collapses to single column on <768px

#### 3. Prompt Box Component
- **Features**:
  - Text input with placeholder: "Ask about crops, prices, or rotation plans..."
  - 3 suggestion chips above input (e.g., "Best crop for wet soil?")
  - Submit button with loading state (progress bar during processing)
  - Auto-focus on page load
- **State**: Manages query text, loading state, error messages
- **API**: POST /api/query with {query: string, aoi: {lat, lng}}

#### 4. Map Component (Leaflet)
- **Base Map**: OpenStreetMap tiles (free, no API key)
- **Overlays**:
  - User location marker (blue pin)
  - NDVI heatmap layer (generated from CSV data, rendered as image overlay)
  - Crop suitability zones (optional, colored polygons)
- **Interactions**: Pan, zoom, geolocation button to detect user location
- **Data Source**: Receives overlay data from backend response

#### 5. Dashboard Component
- **Dynamic Rendering**:
  - Primary: Tembo AI SDK for generative UI (bar graphs, pie charts, lists)
  - Fallback: React Recharts components if Tembo fails
- **Content Types**:
  - Bar graphs: Price trends over years (X: year, Y: price INR/kg)
  - Pie charts: Soil composition (humidity %, sunlight hours, salt content)
  - Lists: Top 3 crop recommendations with reasons, rotation plans
  - Text cards: Sustainability tips, premium feature prompts
- **State**: Updates based on backend response, maintains scroll position

#### 6. Location Selector Component
- **Auto-detection**: Browser Geolocation API on mount
- **Manual Input**: Dropdown or text input for district/city name
- **Default**: Greater Noida, Uttar Pradesh (28.4744° N, 77.5040° E)
- **Validation**: Checks if AOI has available data, suggests nearby locations if not

### Backend Endpoints

#### POST /api/query
- **Request Body**:
  ```json
  {
    "query": "Best crop for wet soil in Greater Noida?",
    "aoi": {"lat": 28.4744, "lng": 77.5040}
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "intent": "crop_recommendation",
      "recommendations": [
        {
          "crop": "Rice",
          "score": 0.85,
          "reasons": ["Suits wet soil", "High demand predicted"],
          "price_range": "25-30 INR/kg",
          "sustainability_note": "Rotate with legumes to maintain nitrogen"
        }
      ],
      "dashboard": {
        "graphs": [...],
        "charts": [...],
        "lists": [...]
      },
      "map_overlays": {
        "ndvi_heatmap_url": "/static/ndvi_greater_noida.png"
      }
    }
  }
  ```
- **Processing Time**: <5 seconds
- **Error Handling**: Returns 400 for invalid queries, 404 for unavailable AOI data

#### GET /api/location/detect
- **Purpose**: Reverse geocode lat/lng to district name
- **Response**: {"district": "Greater Noida", "state": "Uttar Pradesh"}

#### GET /api/data/sources
- **Purpose**: Return list of data sources for attribution
- **Response**: Array of {name, url, description}

### AI Engine Interfaces

#### CropRecommender Class
```python
class CropRecommender:
    def __init__(self, fused_data: pd.DataFrame):
        self.data = fused_data

    def recommend(self, aoi: dict, soil_type: str, humidity: float) -> List[Recommendation]:
        # Rule-based scoring
        # Returns top 3 crops with scores and reasons
        pass
```

#### PricePredictor Class
```python
class PricePredictor:
    def __init__(self, mandi_data: pd.DataFrame):
        self.data = mandi_data

    def predict(self, crop: str, aoi: dict) -> PricePrediction:
        # Linear regression on last 3 years
        # Returns price range and trend
        pass
```

#### RotationPlanner Class
```python
class RotationPlanner:
    def generate_plan(self, current_crop: str, soil_type: str) -> List[SeasonalCrop]:
        # Alternates nutrient-depleting and nitrogen-fixing crops
        # Returns seasonal sequence (Rabi, Kharif, Zaid)
        pass
```

## Data Models

### Frontend TypeScript Types

```typescript
interface AOI {
  lat: number;
  lng: number;
  district?: string;
  state?: string;
}

interface Query {
  text: string;
  aoi: AOI;
  timestamp: Date;
}

interface CropRecommendation {
  crop: string;
  score: number;
  reasons: string[];
  price_range: string;
  sustainability_note: string;
}

interface DashboardData {
  graphs: GraphConfig[];
  charts: ChartConfig[];
  lists: ListConfig[];
}

interface QueryResponse {
  success: boolean;
  data: {
    intent: 'crop_recommendation' | 'price_prediction' | 'rotation_planning';
    recommendations?: CropRecommendation[];
    price_predictions?: PricePrediction[];
    rotation_plan?: SeasonalCrop[];
    dashboard: DashboardData;
    map_overlays: MapOverlays;
  };
  error?: string;
}
```

### Backend Pydantic Models

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class AOIModel(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    district: Optional[str] = None
    state: Optional[str] = None

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    aoi: AOIModel

class IntentType(str, Enum):
    CROP_RECOMMENDATION = "crop_recommendation"
    PRICE_PREDICTION = "price_prediction"
    ROTATION_PLANNING = "rotation_planning"

class CropRecommendationModel(BaseModel):
    crop: str
    score: float = Field(..., ge=0, le=1)
    reasons: List[str]
    price_range: str
    sustainability_note: str

class QueryResponse(BaseModel):
    success: bool
    data: dict
    error: Optional[str] = None
```

### Data CSV Schemas

#### Satellite Data (satellite_ndvi.csv)
```
lat,lng,ndvi,date,source
28.4744,77.5040,0.65,2024-01-15,Landsat-8
```

#### Soil Data (soil_factors.csv)
```
district,state,soil_type,humidity,sunlight_hours,salt_content
Greater Noida,Uttar Pradesh,wet,65,8.5,low
```

#### Mandi Prices (mandi_prices.csv)
```
crop,district,state,price_inr_per_kg,date,market
Rice,Greater Noida,Uttar Pradesh,28.50,2024-01-15,Noida Mandi
```

#### Weather Data (weather.csv)
```
district,state,date,rainfall_mm,temp_celsius,humidity_percent
Greater Noida,Uttar Pradesh,2024-01-15,5.2,18.5,65
```

### Data Fusion Logic

```python
def fuse_data(aoi: AOIModel) -> pd.DataFrame:
    # Load all CSVs
    satellite_df = pd.read_csv('data/satellite_ndvi.csv')
    soil_df = pd.read_csv('data/soil_factors.csv')
    mandi_df = pd.read_csv('data/mandi_prices.csv')
    weather_df = pd.read_csv('data/weather.csv')

    # Filter by AOI (district-level)
    district = reverse_geocode(aoi.lat, aoi.lng)

    # Join on district
    fused = soil_df[soil_df['district'] == district].merge(
        weather_df[weather_df['district'] == district],
        on='district'
    ).merge(
        mandi_df[mandi_df['district'] == district],
        on='district'
    )

    # Add satellite data (nearest lat/lng)
    fused['ndvi'] = get_nearest_ndvi(satellite_df, aoi.lat, aoi.lng)

    return fused
```

## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system - essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

The following properties define the correctness criteria for Orbital Nexus MVP. Each property is universally quantified (applies to all valid inputs) and references the specific requirements it validates.

### Property 1: Geolocation Fallback Consistency

For any geolocation failure (denied, timeout, error, or unavailable), the system should default to Greater Noida, Uttar Pradesh (28.4744° N, 77.5040° E) as the AOI.

**Validates: Requirements 1.2**

### Property 2: Map State Consistency

For any AOI change (detected, manually set, or reset), the map visualization should center on the new location and all overlays (NDVI heatmap, crop zones) should update to reflect data for that AOI within 3 seconds.

**Validates: Requirements 1.3, 1.5, 7.2, 7.6**

### Property 3: Query Suggestion Presence

For any state where the prompt box is visible, exactly 3 query suggestions should be displayed to the user.

**Validates: Requirements 2.2**

### Property 4: Query Intent Classification

For any valid query string submitted by a user, the parserlassify it into exactly one of three intent categories: crop_recommendation, price_prediction, or rotation_planning.

**Validates: Requirements 2.4**

### Property 5: Performance Bounds

For any user query (crop recommendation, price prediction, or rotation planning), the system should complete processing and return a response within 5 seconds, and the dashboard should update within 2 seconds of receiving the response.

**Validates: Requirements 2.5, 3.7, 6.7, 10.3**

### Property 6: Data Fusion Correctness

For any AOI query, the fused dataset should contain only records matching that AOI's district, and all required data sources (satellite, soil, weather, mandi prices) should be joined correctly by location.

**Validates: Requirements 3.5, 3.6**

### Property 7: Recommendation Completeness

For any crop recommendation generated, the result should include all required fields: crop name, confidence score (0-1), at least one reason, price range, and a sustainability note.

**Validates: Requirements 4.5, 4.6, 8.3**

### Property 8: Top-N Recommendation Constraint

For any crop recommendation query, the system should return exactly 3 crop recommendations, each with a valid confidence score between 0 and 1, ordered by score descending.

**Validates: Requirements 4.4**

### Property 9: Price Prediction Data Coverage

For any price prediction query for a specific crop, the system should retrieve historical mandi price data covering at least 3 years (36 months) for that crop in the user's AOI.

**Validates: Requirements 5.1**

### Property 10: Price Prediction Format Consistency

For any price prediction generated, the output should include a price range in the format "X-Y INR/kg" and a percentage change from the most recent historical price.

**Validates: Requirements 5.3**

### Property 11: Overproduction Risk Flagging

For any price prediction where historical supply data shows yield 20% above the 3-year average, the system should flag a potential price drop risk in the response.

**Validates: Requirements 5.4**

### Property 12: Dashboard Generation for Query Types

For any query, the dashboard should generate appropriate visualizations: bar graphs for price queries, pie charts for soil queries, and ordered lists for rotation queries.

**Validates: Requirements 6.2, 6.3, 6.4**

### Property 13: Tembo SDK Fallback

For any dashboard generation request, if Tembo AI SDK fails or is unavailable, the system should fallback to React Recharts components without throwing errors or displaying broken UI.

**Validates: Requirements 6.6**

### Property 14: Map Overlay Offline Operation

For any map rendering, the system should generate all overlays (NDVI heatmap, crop zones) without making external API calls to raster tile services.

**Validates: Requirements 7.5**

### Property 15: Rotation Plan Alternation

For any rotation plan generated, the seasonal crop sequence should alternate between nutrient-depleting crops (e.g., rice, wheat) and nitrogen-fixing crops (e.g., legumes, pulses).

**Validates: Requirements 8.2**

### Property 16: Rotation Plan Contextual Relevance

For any rotation plan generated, the crop suggestions should be based on the user's AOI soil type and historical crop performance data for that location.

**Validates: Requirements 8.5**

### Property 17: Premium Feature Modal Display

For any attempt to access a premium feature (detailed geopolitics analysis, advanced market trends), the system should display a modal explaining premium benefits without granting access.

**Validates: Requirements 9.3**

### Property 18: Feature Access Control

For any feature in the system, it should be clearly labeled with a visual indicator showing whether it is free or premium, and premium features should not be accessible without upgrade.

**Validates: Requirements 9.5**

### Property 19: Mobile Responsiveness

For any viewport width between 320px and 768px, the system should remain functional with all core features (query input, dashboard, map) accessible and usable.

**Validates: Requirements 10.5**

### Property 20: Privacy Preservation

For any user interaction, the system should not transmit personal data (location, queries, preferences) to external servers beyond the local backend, and should not persist data beyond browser session storage.

**Validates: Requirements 11.3**

### Property 21: Guidance Language Consistency

For any recommendation or prediction text displayed to users, the language should use guidance terms (e.g., "consider", "may", "suggested") rather than absolute predictions (e.g., "must", "will", "guaranteed").

**Validates: Requirements 11.5**

### Property 22: Graceful Error Handling

For any invalid query (empty string, malformed input, unsupported intent), the system should return a user-friendly error message without displaying technical stack traces or crashing.

**Validates: Requirements 12.1**

### Property 23: Missing Data Fallback

For any AOI query where data is unavailable, the system should display a helpful message suggesting nearby locations with available data, rather than showing empty results or errors.

**Validates: Requirements 12.2**

### Property 24: Error Logging Without User Exposure

For any error that occurs during query processing, the system should log the error details to the browser console for debugging, but should only display a user-friendly message to the user.

**Validates: Requirements 12.4**

## Error Handling

### Frontend Error Handling

1. **Geolocation Errors**
   - Timeout: Fallback to default location after 5 seconds
   - Permission denied: Show message "Location access denied, using default location"
   - Position unavailable: Fallback to default location
   - All errors: Log to console, continue with default

2. **API Request Errors**
   - Network failure: Show "Unable to connect, please check your connection"
   - 400 Bad Request: Show "Invalid query, please try rephrasing"
   - 404 Not Found: Show "No data available for this location, try nearby areas"
   - 500 Server Error: Show "Something went wrong, please try again"
   - Timeout (>10s): Show "Request timed out, please try again"

3. **Map Rendering Errors**
   - Tile loading failure: Use fallback base map
   - Overlay generation failure: Show map without overlays, log error
   - Invalid coordinates: Center on default location

4. **Dashboard Rendering Errors**
   - Tembo SDK failure: Fallback to Recharts components
   - Invalid data format: Show "Unable to display visualization" placeholder
   - Component crash: Use error boundary to show fallback UI

### Backend Error Handling

1. **Data Loading Errors**
   - CSV file not found: Log error, return 500 with message "Data unavailable"
   - CSV parsing error: Log error, skip corrupted rows, continue with valid data
   - Insufficient data: Return 404 with message "No data for this location"

2. **Query Processing Errors**
   - Intent classification failure: Default to crop_recommendation intent
   - Empty query: Return 400 with message "Please enter a query"
   - Query too long (>500 chars): Return 400 with message "Query too long, please shorten"

3. **AI Engine Errors**
   - No matching crops: Return message "No suitable crops found for these conditions"
   - Price prediction failure: Return message "Price data unavailable for this crop"
   - Rotation plan failure: Return generic rotation plan based on soil type only

4. **Data Fusion Errors**
   - Join failure: Log error, return partial data with warning
   - Missing columns: Use default values, log warning
   - Data type mismatch: Coerce types, log warning

### Error Response Format

All backend errors follow consistent format:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "User-friendly message",
    "details": {} // Optional, for debugging
  }
}
```

Error codes:
- INVALID_QUERY: Malformed or empty query
- DATA_UNAVAILABLE: No data for requested AOI
- PROCESSING_ERROR: Internal processing failure
- TIMEOUT: Request exceeded time limit

## Testing Strategy

### Dual Testing Approach

Orbital Nexus will use both unit testing and property-based testing to ensure comprehensive coverage:

- **Unit tests**: Verify specific examples, edge cases, and error conditions
- **Property tests**: Verify universal properties across all inputs

Both testing approaches are complementary and necessary. Unit tests catch concrete bugs in specific scenarios, while property tests verify general correctness across a wide range of inputs.

### Property-Based Testing Configuration

**Library Selection**:
- Frontend: fast-check (TypeScript/JavaScript property testing library)
- Backend: Hypothesis (Python property testing library)

**Test Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Each property test must reference its design document property
- Tag format: `Feature: orbital-nexus-mvp, Property {number}: {property_text}`

**Property Test Implementation**:
- Each correctness property (1-24) must be implemented as a single property-based test
- Tests should generate random valid inputs within the domain
- Tests should verify the property holds for all generated inputs
- Tests should fail fast and report counterexamples clearly

### Unit Testing Strategy

**Frontend Unit Tests** (Jest + React Testing Library):
1. Component rendering tests
   - Landing page sections render correctly
   - SPA layout components mount without errors
   - Prompt box displays with suggestions
   - Map initializes with default location

2. User interaction tests
   - Query submission triggers API call
   - Location selector updates AOI
   - Dashboard scrolls and displays content
   - Premium modal opens on feature access

3. Edge case tests
   - Empty query handling
   - Invalid coordinates handling
   - Missing data handling
   - Network failure handling

**Backend Unit Tests** (Pytest):
1. Endpoint tests
   - POST /api/query returns valid response
   - GET /api/location/detect returns district
   - Error responses have correct format

2. Data fusion tests
   - CSV loading succeeds for all files
   - Join operations produce correct results
   - Filtering by AOI returns correct subset

3. AI engine tests
   - CropRecommender returns top 3 crops
   - PricePredictor calculates trends correctly
   - RotationPlanner alternates crop types

4. Edge case tests
   - Missing CSV files
   - Empty datasets
   - Invalid AOI coordinates
   - Malformed queries

### Integration Testing

**End-to-End Flow Tests**:
1. User enters query → Backend processes → Dashboard updates
2. User changes location → Map updates → Data refetches
3. User accesses premium feature → Modal displays
4. User resets demo → State clears → Returns to default

**Performance Tests**:
1. Query processing completes within 5 seconds
2. Dashboard updates within 2 seconds
3. Map overlays render within 3 seconds
4. Initial page load completes within 5 seconds

### Test Coverage Goals

- Minimum overall coverage: 80%
- Critical paths (query processing, data fusion, AI engine): 90%+
- Error handling paths: 85%+

### Testing During Hackathon

Given the 36-hour timeline, prioritize:
1. Property tests for core correctness properties (1-10)
2. Unit tests for critical paths (query processing, recommendations)
3. Manual testing for UI/UX and demo flow
4. Integration tests for end-to-end scenarios

Defer to post-hackathon:
- Comprehensive edge case unit tests
- Performance optimization tests
- Accessibility tests
- Cross-browser compatibility tests

### Definition of Done

A feature is complete when:
1. All property tests pass (100 iterations each)
2. Unit tests pass for critical paths
3. Manual testing confirms demo stability
4. Error handling works gracefully
5. No regressions in existing features
6. Code is committed to Git with clear messages

## Deployment Strategy

### Development Environment

**Local Development**:
- Frontend: `npm run dev` (Vite dev server on port 3000)
- Backend: `uvicorn main:app --reload` (FastAPI on port 8000)
- Data: CSV files in /data folder (committed to Git)

**Environment Variables**:
```bash
# Frontend (.env)
VITE_API_URL=http://localhost:8000
VITE_DEFAULT_LAT=28.4744
VITE_DEFAULT_LNG=77.5040

# Backend (.env)
DATA_DIR=./data
CORS_ORIGINS=http://localhost:3000,https://orbitalnexus.online
```

### Production Deployment

**Hosting**: Hostinger (orbitalnexus.online)

**Build Process**:
1. Frontend: `npm run build` → Static files in /dist
2. Backend: Package with dependencies → Deploy as Python app
3. Data: Upload CSV files to server /data directory

**Deployment Steps**:
1. Build frontend: `cd frontend && npm run build`
2. Upload frontend /dist to Hostinger public_html
3. Upload backend files to Hostinger Python app directory
4. Upload /data folder to server
5. Configure environment variables in Hostinger panel
6. Start backend service
7. Test live site: https://orbitalnexus.online

**Alternative Quick Deployment** (for hackathon):
- Frontend: Deploy to Vercel/Netlify (auto-deploy from Git)
- Backend: Deploy to Railway/Render (free tier)
- Point domain to deployed services

### Health Checks

**Backend Health Endpoint**:
```python
@app.get("/health")
async def health_check():
    # Verify data files exist
    data_files = ["satellite_ndvi.csv", "soil_factors.csv", "mandi_prices.csv", "weather.csv"]
    missing = [f for f in data_files if not os.path.exists(f"data/{f}")]

    if missing:
        return {"status": "unhealthy", "missing_files": missing}

    return {"status": "healthy", "data_files": len(data_files)}
```

**Frontend Health Check**:
- Verify API connectivity on mount
- Display warning banner if backend unreachable
- Fallback to cached demo data if offline

### Monitoring

**Hackathon Monitoring** (minimal):
- Browser console for frontend errors
- Backend logs for API errors
- Manual testing before mentor rounds

**Post-Hackathon Monitoring**:
- Error tracking (Sentry)
- Analytics (Google Analytics)
- Performance monitoring (Web Vitals)
- API usage metrics

## Security Considerations

### Data Security

1. **No Sensitive Data**: System uses only public datasets, no user authentication required
2. **No Data Persistence**: User queries and preferences stored only in browser session storage
3. **No External Transmission**: Location and query data sent only to local backend, not third parties

### Input Validation

1. **Query Validation**: Max 500 characters, sanitize HTML/SQL injection attempts
2. **Coordinate Validation**: Lat (-90 to 90), Lng (-180 to 180)
3. **File Upload**: Not supported (all data pre-loaded)

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://orbitalnexus.online"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Rate Limiting

**Hackathon**: Not implemented (demo environment)

**Production**: Implement rate limiting (10 requests/minute per IP) to prevent abuse

## Accessibility

### WCAG 2.1 Level AA Compliance

1. **Keyboard Navigation**: All interactive elements accessible via keyboard
2. **Screen Reader Support**: ARIA labels on all UI components
3. **Color Contrast**: Minimum 4.5:1 ratio for text, 3:1 for UI components
4. **Focus Indicators**: Visible focus outlines on all interactive elements
5. **Alt Text**: Descriptive alt text for all images and visualizations

### Responsive Design

- Mobile-first approach (320px minimum width)
- Touch-friendly targets (minimum 44x44px)
- Readable text sizes (minimum 16px body text)
- Collapsible sidebar on mobile (<768px)

### Language Support

**MVP**: English only

**Post-Hackathon**: Add Hindi support for farmer accessibility
- UI translations
- Query parsing in Hindi
- Recommendations in Hindi

## Future Enhancements

### Phase 2 (Post-Hackathon)

1. **Real-Time Data Integration**
   - Register for Agmarknet API for live mandi prices
   - Integrate weather forecast APIs
   - Add satellite data refresh pipeline

2. **Advanced AI Features**
   - Machine learning models for crop recommendations (replace rule-based)
   - Time series forecasting for price predictions (replace linear regression)
   - Geopolitics impact analysis (trade blocks, import/export)

3. **User Features**
   - User authentication and profiles
   - Save favorite queries and locations
   - Notification system for price alerts
   - Multi-language support (Hindi, Punjabi, Bengali)

4. **Business Features**
   - Payment integration for premium subscriptions
   - Partnership integrations (fertilizer distributors, government schemes)
   - Farmer community forum
   - Expert consultation booking

5. **Technical Improvements**
   - Database migration (MongoDB for user data)
   - Caching layer (Redis for query results)
   - CDN for static assets
   - Progressive Web App (PWA) for offline support

### Phase 3 (Scale)

1. **Geographic Expansion**: Cover all Indian states with localized data
2. **Crop Database**: Expand from 10-15 crops to 100+ crops
3. **IoT Integration**: Connect with soil sensors and weather stations
4. **Mobile Apps**: Native iOS and Android apps
5. **API Platform**: Offer API access for third-party integrations

## Appendix

### Technology Justification

**React 19**: Latest stable version, excellent ecosystem, fast development
**TypeScript**: Type safety reduces bugs, better IDE support
**TailwindCSS**: Rapid UI development, consistent design system
**Leaflet**: Lightweight, open-source, no API keys required
**FastAPI**: Fast, modern Python framework, auto-generated docs
**Pandas**: Industry standard for data manipulation, excellent CSV support
**Hypothesis/fast-check**: Mature property testing libraries, good documentation

### Dataset Sources

1. **Landsat Satellite Data**: https://www.kaggle.com/datasets/elshadai/landsat-satellite-data-set
2. **Crop Recommendation Dataset**: https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset
3. **Soil-Climate Data**: https://www.kaggle.com/datasets/rajeev86/soil-climate-data
4. **Daily Wholesale Prices**: https://www.kaggle.com/datasets/ishankat/daily-wholesale-commodity-prices-india-mandis
5. **Indian Historical Crop Yield**: https://www.kaggle.com/datasets/zoya77/indian-historical-crop-yield-and-weather-data

### Team Responsibilities

- **Anand Vashishtha**: Overall coordination, backend development, deployment
- **Dheershikha**: Frontend UI/UX, landing page, SPA components
- **Harsh Kumar Sharma**: AI engine, data fusion, recommendation algorithms
- **Manvendra Singh**: Data collection, CSV preparation, data fusion logic
- **Mansi Yadav**: Pitch deck, promotion, social media, demo presentation

### Hackathon Timeline Integration

- **3:00 PM - 4:00 PM**: Setup project structure, download datasets
- **4:00 PM - 5:30 PM**: Mentor Round 1 - Demo basic query/response
- **5:30 PM - 9:00 PM**: Build core features (data fusion, AI engine, frontend)
- **9:00 PM - 10:00 PM**: Dinner break, code review
- **10:00 PM - 1:30 AM**: Integration, dashboard, map visualization
- **1:30 AM - 3:30 AM**: Mentor Round 2 - Full demo, refinement
- **3:30 AM - 9:00 AM**: Polish, deployment, testing
- **9:00 AM - 10:30 AM**: Final testing, pitch rehearsal
- **10:30 AM - 1:00 PM**: Judging and presentation
