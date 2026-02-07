# System Architecture: Orbital Nexus

## Overview

Orbital Nexus follows a three-tier architecture with clear separation between presentation (React SPA), business logic (FastAPI backend), and data (offline CSV files). The system is designed for offline-first operation with no external API dependencies during query processing.

## Architecture Layers

### 1. Presentation Layer (Frontend)

**Technology**: React 19, TypeScript, TailwindCSS, Leaflet, Recharts, Framer Motion

**Components**:
- **Landing Page**: Scrollable marketing page with hero, problem, solution, business model, impact sections
- **SPA Layout**: Full-screen application with logo, map, dashboard, and prompt box
- **Prompt Box**: ChatGPT-style input with query suggestions and progress bar
- **Map Component**: Leaflet 2D map with OpenStreetMap tiles, location markers, NDVI heatmap overlays
- **Dashboard Component**: Scrollable sidebar with dynamic visualizations (bar graphs, pie charts, lists)
- **Location Selector**: Browser geolocation API with manual override option

**Responsibilities**:
- User interaction handling (query input, location selection)
- API communication (POST /api/query, GET /api/location/detect)
- Visualization rendering (maps, graphs, charts)
- Error handling and loading states
- Responsive design (mobile-first, 320px minimum)

### 2. API Layer (Backend)

**Technology**: Python 3.12, FastAPI, Pydantic

**Endpoints**:
- **POST /api/query**: Process user queries, return recommendations and dashboard data
- **GET /api/location/detect**: Reverse geocode lat/lng to district name
- **GET /api/data/sources**: Resource attributions
- **GET /health**: Health check endpoint

**Responsibilities**:
- Query parsing and intent classification
- Request validation (Pydantic models)
- Response formatting (consistent JSON structure)
- Error handling and logging
- CORS configuration for frontend access

### 3. Business Logic Layer (AI Engine)

**Technology**: Python 3.12, NumPy, Pandas

**Classes**:
- **CropRecommender**: Rule-based scoring for crop recommendations
- **PricePredictor**: Linear regression for price trend predictions
- **RotationPlanner**: Seasonal crop sequence generator
- **DataFusion**: Multi-source dataset joining and filtering

**Responsibilities**:
- Crop recommendation logic (soil type, humidity, sunlight, salt, weather, prices)
- Price prediction calculations (3-year historical trends, linear regression)
- Rotation plan generation (alternating nutrient-depleting and nitrogen-fixing crops)
- Data fusion (join satellite, soil, weather, mandi price datasets by location)

### 4. Data Layer

**Technology**: Pandas, CSV files

**Datasets**:
- **satellite_ndvi.csv**: NDVI values from Landsat/Sentinel (lat, lng, ndvi, date, source)
- **soil_factors.csv**: Soil characteristics (district, state, soil_type, humidity, sunlight_hours, salt_content)
- **mandi_prices.csv**: Historical wholesale prices (crop, district, state, price_inr_per_kg, date, market)
- **weather.csv**: Weather data (district, state, date, rainfall_mm, temp_celsius, humidity_percent)

**Responsibilities**:
- CSV file loading and parsing
- Data validation (check required columns)
- Location-based filtering (district-level precision)
- Dataset joining (Pandas merge operations)
- Caching for default location (Greater Noida)

## Data Flow

### Query Processing Flow

1. **User Input**: User enters query in prompt box (e.g., "Best crop for wet soil in Greater Noida?")
2. **Frontend Validation**: Check query length (<500 chars), show loading state
3. **API Request**: POST /api/query with {query: string, aoi: {lat, lng}}
4. **Backend Parsing**: Classify intent (crop_recommendation, price_prediction, rotation_planning)
5. **Data Fusion**: Load and join datasets filtered by user's AOI (district)
6. **AI Processing**:
   - Crop recommendation: Apply rule-based scoring, select top 3 crops
   - Price prediction: Calculate linear trend on 3-year historical data
   - Rotation planning: Generate seasonal sequence with alternation
7. **Response Formatting**: Structure response with recommendations, dashboard data, map overlays
8. **Frontend Rendering**: Update dashboard (graphs, charts, lists) and map (overlays)
9. **Total Time**: <5 seconds from query submission to dashboard update

### Location Detection Flow

1. **Page Load**: SPA mounts, triggers geolocation API call
2. **Geolocation Success**: Browser returns lat/lng → Display on map, set as AOI
3. **Geolocation Failure**: Fallback to Greater Noida (28.4744° N, 77.5040° E)
4. **Manual Override**: User selects location from dropdown → Update AOI, refetch data
5. **Map Update**: Center map on new AOI, update overlays within 3 seconds

### Data Fusion Flow

1. **Load CSVs**: Read all 4 CSV files into Pandas DataFrames
2. **Reverse Geocode**: Convert user's lat/lng to district name
3. **Filter by District**: Select rows matching user's district from each dataset
4. **Join Datasets**: Merge soil, weather, mandi price data on district
5. **Add Satellite Data**: Find nearest NDVI value by lat/lng proximity
6. **Return Fused Data**: Single DataFrame with all factors for user's location
7. **Cache**: Store fused data for Greater Noida for instant demo responses

## Component Interactions

### Frontend → Backend

**Request Format**:
```json
{
  "query": "Best crop for wet soil?",
  "aoi": {"lat": 28.4744, "lng": 77.5040}
}
```

**Response Format**:
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
        "sustainability_note": "Rotate with legumes"
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

### Backend → Data Layer

**Query Pattern**:
```python
# Load data
soil_df = pd.read_csv('data/soil_factors.csv')
mandi_df = pd.read_csv('data/mandi_prices.csv')

# Filter by AOI
district = reverse_geocode(aoi.lat, aoi.lng)
fused = soil_df[soil_df['district'] == district].merge(
    mandi_df[mandi_df['district'] == district],
    on='district'
)
```

### AI Engine → Data Layer

**Recommendation Logic**:
```python
# Rule-based scoring
score = 0
if soil_type == 'wet' and humidity > 60:
    score += 0.3  # Rice prefers wet soil
if sunlight_hours > 8:
    score += 0.2  # Rice needs sunlight
if avg_price > threshold:
    score += 0.2  # High demand
```

## Deployment Architecture

### Development

- **Frontend**: Vite dev server (localhost:3000)
- **Backend**: Uvicorn (localhost:8000)
- **Data**: Local /data folder

### Production

- **Frontend**: Static files on Hostinger public_html or Vercel
- **Backend**: Python app on Hostinger or Railway/Render
- **Data**: CSV files uploaded to server /data directory
- **Domain**: orbitalnexus.online (points to frontend)
- **API**: Backend URL configured in frontend environment variables

## Scalability Considerations

### Current (MVP)

- Single-server deployment
- CSV file storage
- No caching beyond pre-computed Greater Noida results
- No load balancing

### Future (Post-Hackathon)

- Database migration (MongoDB for user data, PostgreSQL for structured data)
- Redis caching for frequent queries
- CDN for static assets
- Horizontal scaling with load balancer
- Real-time data pipelines for satellite and mandi price updates

## Security Architecture

### Current (MVP)

- No authentication (open access)
- CORS restricted to frontend domain
- Input validation (query length, coordinate ranges)
- No data persistence (session storage only)
- No external data transmission

### Future (Post-Hackathon)

- JWT authentication for user accounts
- Rate limiting (10 requests/minute per IP)
- API key for premium features
- HTTPS only (SSL certificate)
- Data encryption at rest and in transit

## Error Handling Architecture

### Frontend

- Error boundaries for component crashes
- Fallback UI for missing data
- User-friendly error messages
- Retry logic for API failures

### Backend

- Try-catch blocks on all endpoints
- Consistent error response format
- Logging to console (no external services)
- Graceful degradation (partial data on join failures)

### Data Layer

- File existence checks before loading
- CSV parsing error handling (skip corrupted rows)
- Default values for missing columns
- Validation of data types and ranges

## Monitoring and Observability

### Hackathon (Minimal)

- Browser console for frontend errors
- Backend logs for API errors
- Manual testing before mentor rounds

### Production (Future)

- Error tracking (Sentry)
- Performance monitoring (Web Vitals)
- API usage metrics (request counts, response times)
- User analytics (Google Analytics)

## Technology Justification

- **React 19**: Latest stable, excellent ecosystem, fast development
- **TypeScript**: Type safety reduces bugs, better IDE support
- **TailwindCSS**: Rapid UI development, consistent design system
- **Leaflet**: Lightweight, open-source, no API keys required
- **FastAPI**: Fast, modern Python framework, auto-generated docs
- **Pandas**: Industry standard for data manipulation, excellent CSV support
- **Offline-first**: No external dependencies, demo stability, rural connectivity
