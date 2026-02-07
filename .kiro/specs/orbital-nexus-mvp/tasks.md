# Implementation Plan: Orbital Nexus MVP

##

This implementation plan breaks down the Orbital Nexus MVP into discrete coding tasks for a 36-hour hackathon build. The plan prioritizes demo-ready features, visual impact, and stability for judging. Tasks are organized to enable parallel work across team members and include checkpoints for mentor feedback rounds.

The implementation uses:
- **Frontend**: React 19, TypeScript, TailwindCSS, Leaflet, Recharts
- **Backend**: Python 3.12, FastAPI, Pandas, NumPy
- **Data**: Offline CSV files in /data folder

## Tasks

- [ ] 1. Project Setup and Data Preparation
  - Create project directory structure (frontend/, backend/, data/)
  - Initialize Git repository with .gitignore
  - Setup frontend: Create React app with Vite, install dependencies (react, typescript, tailwindcss, leaflet, recharts, framer-motion, axios)
  - Setup backend: Create FastAPI project structure, install dependencies (fastapi, uvicorn, pandas, numpy, pydantic, python-multipart)
  - Download and organize CSV datasets in /data folder (satellite_ndvi.csv, soil_factors.csv, mandi_prices.csv, weather.csv)
  - Create README.md with project overview and setup instructions
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 10.1_

- [ ] 2. Backend Data Layer Implementation
  - [ ] 2.1 Create data loading module
    - Write functions to load all CSV files using Pandas
    - Implement error handling for missing or corrupted files
    - Add data validation (check required columns exist)
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [ ]* 2.2 Write property test for data loading
    - **Property 6: Data Fusion Correctness**
    - **Validates: Requirements 3.5, 3.6**

  - [ ] 2.3 Implement data fusion logic
    - Write function to join datasets by location (district-level)
    - Implement filtering by AOI (latitude/longitude matching)
    - Add caching for Greater Noida (default location) for instant demo
    - _Requirements: 3.5, 3.6, 3.7_

  - [ ]* 2.4 Write property test for data fusion
    - Test that fused data contains only records for queried AOI
    - Test that all data sources are joined correctly
    - _Requirements: 3.5, 3.6_

- [ ] 3. Backend AI Engine Implementation
  - [ ] 3.1 Implement CropRecommender class
    - Write rule-based scoring algorithm (soil type, humidity, sunlight, salt)
    - Implement top-3 crop selection with confidence scores
    - Add reason generation for each recommendation
    - Include sustainability notes
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [ ]* 3.2 Write property tests for crop recommendations
    - **Property 7: Recommendation Completeness**
    - **Property 8: Top-N Recommendation Constraint**
    - **Validates: Requirements 4.4, 4.5, 4.6**

  - [ ] 3.3 Implement PricePredictor class
    - Write function to retrieve 3 years of historical mandi prices
    - Implement linear regression for price trend prediction
    - Format predictions as price ranges with percentage change
    - Add overproduction risk flagging logic
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ]* 3.4 Write property tests for price predictions
    - **Property 9: Price Prediction Data Coverage**
    - **Property 10: Price Prediction Format Consistency**
    - **Property 11: Overproduction Risk Flagging**
    - **Validates: Requirements 5.1, 5.3, 5.4**

  - [ ] 3.5 Implement RotationPlanner class
    - Write function to generate seasonal crop sequences
    - Ensure alternation between nutrient-depleting and nitrogen-fixing crops
    - Base suggestions on soil type and historical performance
    - _Requirements: 8.1, 8.2, 8.5_

  - [ ]* 3.6 Write property tests for rotation planning
    - **Property 15: Rotation Plan Alternation**
    - **Property 16: Rotation Plan Contextual Relevance**
    - **Validates: Requirements 8.2, 8.5**

- [ ] 4. Backend API Endpoints
  - [ ] 4.1 Create FastAPI application structure
    - Setup main.py with CORS middleware
    - Create Pydantic models for requests/responses (AOIModel, QueryRequest, QueryResponse)
    - Add health check endpoint
    - _Requirements: 11.1_

  - [ ] 4.2 Implement POST /api/query endpoint
    - Parse query intent (crop_recommendation, price_prediction, rotation_planning)
    - Call appropriate AI engine class based on intent
    - Format response with recommendations and dashboard data
    - Add error handling for invalid queries and missing data
    - _Requirements: 2.4, 2.5, 12.1, 12.2_

  - [ ]* 4.3 Write property tests for query endpoint
    - **Property 4: Query Intent Classification**
    - **Property 5: Performance Bounds**
    - **Property 22: Graceful Error Handling**
    - **Property 23: Missing Data Fallback**
    - **Validates: Requirements 2.4, 2.5, 12.1, 12.2**

  - [ ] 4.3 Implement GET /api/location/detect endpoint
    - Reverse geocode lat/lng to district name
    - Return district and state information
    - _Requirements: 1.1_

  - [ ]* 4.4 Write unit tests for API endpoints
    - Test valid query processing
    - Test error responses (400, 404, 500)
    - Test response format consistency
    - _Requirements: 2.5, 12.1_

- [ ] 5. Checkpoint - Backend Core Complete
  - Ensure all backend tests pass
  - Manually test API endpoints with Postman/curl
  - Verify data fusion works for Greater Noida
  - Ask user if questions arise

- [ ] 6. Frontend Project Structure
  - [ ] 6.1 Setup React project with Vite
    - Configure TypeScript, TailwindCSS
    - Create folder structure (components/, pages/, services/, hooks/, types/, utils/)
    - Setup routing (React Router for landing page and SPA)
    - _Requirements: N/A_

  - [ ] 6.2 Create TypeScript types
    - Define interfaces (AOI, Query, CropRecommendation, QueryResponse, DashboardData)
    - Create type definitions file (types/index.ts)
    - _Requirements: N/A_

  - [ ] 6.3 Create API client service
    - Setup Axios instance with base URL
    - Create functions for API calls (postQuery, getLocationDetect)
    - Add error handling and timeout configuration
    - _Requirements: 2.5_

- [ ] 7. Frontend Landing Page
  - [ ] 7.1 Create Landing Page component
    - Implement Hero section (logo, tagline, CTA button)
    - Implement Problem section (infographic on supply-demand imbalances)
    - Implement Solution section (feature showcase)
    - Implement Business section (freemium model table)
    - Implement Impact section (sustainability stats)
    - Implement Footer (team info, social handles, data attributions)
    - Style with TailwindCSS (eco-theme: greens/blues)
    - _Requirements: 11.4_

  - [ ]* 7.2 Write unit tests for Landing Page
    - Test all sections render correctly
    - Test CTA button navigation
    - Test responsive layout
    - _Requirements: N/A_

- [ ] 8. Frontend SPA Layout
  - [ ] 8.1 Create SPA Layout component
    - Implement top logo and location indicator
    - Create responsive grid layout (map center-right, dashboard left, prompt bottom)
    - Add mobile responsive breakpoints (<768px single column)
    - _Requirements: 10.5_

  - [ ]* 8.2 Write property test for mobile responsiveness
    - **Property 19: Mobile Responsiveness**
    - **Validates: Requirements 10.5**

- [ ] 9. Frontend Location Detection
  - [ ] 9.1 Create Location Selector component
    - Implement browser geolocation API call on mount
    - Add fallback to Greater Noida on geolocation failure
    - Create manual location input form (dropdown or text)
    - Display current AOI in UI
    - _Requirements: 1.1, 1.2, 1.4_

  - [ ]* 9.2 Write property tests for location detection
    - **Property 1: Geolocation Fallback Consistency**
    - **Validates: Requirements 1.2**

  - [ ]* 9.3 Write unit tests for location selector
    - Test geolocation API call
    - Test fallback to default location
    - Test manual location input
    - _Requirements: 1.1, 1.2, 1.4_

- [ ] 10. Frontend Prompt Box Component
  - [ ] 10.1 Create Prompt Box component
    - Implement text input with placeholder
    - Add 3 query suggestion chips above input
    - Create submit button with loading state (progress bar)
    - Add auto-focus on page load
    - Style with TailwindCSS and Framer Motion for animations
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ]* 10.2 Write property test for query suggestions
    - **Property 3: Query Suggestion Presence**
    - **Validates: Requirements 2.2**

  - [ ]* 10.3 Write unit tests for prompt box
    - Test input handling
    - Test suggestion click
    - Test submit button
    - Test loading state
    - _Requirements: 2.1, 2.2, 2.3_

- [ ] 11. Frontend Map Component
  - [ ] 11.1 Create Map component with Leaflet
    - Initialize Leaflet map with OpenStreetMap tiles
    - Add user location marker
    - Implement map centering on AOI
    - Add geolocation button
    - _Requirements: 7.1, 7.2_

  - [ ] 11.2 Implement map overlays
    - Create NDVI heatmap overlay from backend data
    - Add crop suitability zone overlays (optional)
    - Ensure no external raster tile API calls
    - _Requirements: 7.3, 7.5_

  - [ ]* 11.3 Write property tests for map
    - **Property 2: Map State Consistency**
    - **Property 14: Map Overlay Offline Operation**
    - **Validates: Requirements 1.3, 1.5, 7.2, 7.5, 7.6**

  - [ ]* 11.4 Write unit tests for map component
    - Test map initialization
    - Test marker placement
    - Test overlay rendering
    - _Requirements: 7.1, 7.2, 7.3_

- [ ] 12. Checkpoint - Frontend Core Complete
  - Ensure all frontend components render without errors
  - Test location detection and map display
  - Test prompt box and query submission
  - Ask user if questions arise

- [ ] 13. Frontend Dashboard Component
  - [ ] 13.1 Create Dashboard component structure
    - Implement scrollable left sidebar
    - Create container for dynamic content
    - Add loading state and error boundary
    - _Requirements: 6.1_

  - [ ] 13.2 Implement Recharts visualizations (fallback)
    - Create bar graph component for price trends
    - Create pie chart component for soil composition
    - Create list component for recommendations and rotation plans
    - _Requirements: 6.2, 6.3, 6.4_

  - [ ] 13.3 Integrate Tembo AI SDK (if available)
    - Setup Tembo AI SDK
    - Implement dynamic dashboard generation
    - Add fallback to Recharts on SDK failure
    - _Requirements: 6.5, 6.6_

  - [ ]* 13.4 Write property tests for dashboard
    - **Property 12: Dashboard Generation for Query Types**
    - **Property 13: Tembo SDK Fallback**
    - **Validates: Requirements 6.2, 6.3, 6.4, 6.6**

  - [ ]* 13.5 Write unit tests for dashboard
    - Test bar graph rendering
    - Test pie chart rendering
    - Test list rendering
    - Test error boundary
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 14. Frontend-Backend Integration
  - [ ] 14.1 Connect prompt box to API
    - Implement query submission handler
    - Parse API response and update state
    - Handle loading and error states
    - _Requirements: 2.5_

  - [ ] 14.2 Connect dashboard to API response
    - Parse dashboard data from API response
    - Render appropriate visualizations based on query intent
    - Update dashboard within 2 seconds of response
    - _Requirements: 6.7_

  - [ ] 14.3 Connect map to API response
    - Parse map overlay data from API response
    - Update map overlays based on query results
    - Update map within 3 seconds of AOI change
    - _Requirements: 7.6_

  - [ ]* 14.4 Write integration tests
    - Test end-to-end query flow (input → API → dashboard)
    - Test location change flow (selector → API → map)
    - Test error handling flow
    - _Requirements: 2.5, 6.7, 7.6_

- [ ] 15. Freemium Features Implementation
  - [ ] 15.1 Create Premium Modal component
    - Implement modal with premium benefits explanation
    - Add "Upgrade" button (mock, no payment integration)
    - Style with TailwindCSS
    - _Requirements: 9.2, 9.3_

  - [ ] 15.2 Add feature access control
    - Mark premium features in UI with visual indicators
    - Trigger premium modal on premium feature access
    - Ensure free features remain accessible
    - _Requirements: 9.1, 9.4, 9.5_

  - [ ]* 15.3 Write property tests for freemium features
    - **Property 17: Premium Feature Modal Display**
    - **Property 18: Feature Access Control**
    - **Validates: Requirements 9.3, 9.5**

- [ ] 16. Error Handling and Edge Cases
  - [ ] 16.1 Implement frontend error handling
    - Add error boundaries for component crashes
    - Implement user-friendly error messages for API failures
    - Add fallback UI for missing data
    - _Requirements: 12.1, 12.2, 12.4_

  - [ ] 16.2 Implement backend error handling
    - Add try-catch blocks for all API endpoints
    - Implement consistent error response format
    - Add logging for debugging (console only, no external services)
    - _Requirements: 12.4_

  - [ ]* 16.3 Write property tests for error handling
    - **Property 22: Graceful Error Handling**
    - **Property 23: Missing Data Fallback**
    - **Property 24: Error Logging Without User Exposure**
    - **Validates: Requirements 12.1, 12.2, 12.4**

- [ ] 17. Privacy and Ethical Features
  - [ ] 17.1 Add disclaimers
    - Display disclaimer on landing page and SPA
    - Use guidance language in all recommendations
    - Add data source attributions in footer
    - _Requirements: 11.2, 11.4, 11.5_

  - [ ] 17.2 Implement privacy measures
    - Ensure no data transmission to external servers
    - Use session storage only (no persistent storage)
    - Add privacy policy page (simple, hackathon-appropriate)
    - _Requirements: 11.3_

  - [ ]* 17.3 Write property tests for privacy
    - **Property 20: Privacy Preservation**
    - **Property 21: Guidance Language Consistency**
    - **Validates: Requirements 11.3, 11.5**

- [ ] 18. Demo Stability Features
  - [ ] 18.1 Pre-compute Greater Noida results
    - Generate and cache sample results for default location
    - Ensure instant responses for demo queries
    - _Requirements: 12.3_

  - [ ] 18.2 Add Reset Demo button
    - Create button to clear all state
    - Reset to default Greater Noida location
    - Clear query history and dashboard
    - _Requirements: 12.5_

  - [ ]* 18.3 Write unit tests for demo features
    - Test cached results loading
    - Test reset button functionality
    - _Requirements: 12.3, 12.5_

- [ ] 19. Checkpoint - Full Integration Complete
  - Run all tests (property tests and unit tests)
  - Perform end-to-end manual testing
  - Test on mobile devices
  - Verify demo stability
  - Ask user if questions arise

- [ ] 20. Deployment and Final Polish
  - [ ] 20.1 Build and deploy frontend
    - Run `npm run build` to create production build
    - Deploy to Hostinger or Vercel/Netlify
    - Configure environment variables
    - Test live site
    - _Requirements: N/A_

  - [ ] 20.2 Deploy backend
    - Package backend with dependencies
    - Deploy to Hostinger or Railway/Render
    - Upload CSV data files
    - Configure CORS for production domain
    - Test API endpoints on live server
    - _Requirements: N/A_

  - [ ] 20.3 Final testing and polish
    - Test full flow on live site
    - Fix any deployment issues
    - Optimize performance (lazy loading, code splitting)
    - Add loading spinners and animations
    - _Requirements: 10.2_

  - [ ]* 20.4 Create pitch deck
    - Prepare slides for judging presentation
    - Include problem, solution, demo, impact, business model
    - Practice pitch with team
    - _Requirements: N/A_

- [ ] 21. Final Checkpoint - Production Ready
  - Verify all features work on live site
  - Test on multiple devices and browsers
  - Ensure demo queries work instantly
  - Prepare for judging presentation
  - Celebrate and get ready to present!

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation and mentor feedback
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Prioritize tasks 1-14 for Mentor Round 1 (4:00 PM)
- Complete tasks 15-19 for Mentor Round 2 (1:30 AM)
- Tasks 20-21 for final polish before judging (10:30 AM)

## Team Task Allocation Suggestions

- **Anand**: Tasks 1, 4, 5, 20 (Backend API, deployment, coordination)
- **Harsh**: Tasks 2, 3 (Data layer, AI engine)
- **Manvendra**: Tasks 1, 2 (Data preparation, data fusion)
- **Dheershikha**: Tasks 6, 7, 8, 10, 11, 13 (Frontend UI components)
- **Mansi**: Tasks 7, 15, 20.4 (Landing page, freemium features, pitch deck)

## Hackathon Timeline Alignment

- **3:00 PM - 4:00 PM**: Tasks 1, 2.1, 6.1 (Setup and data prep)
- **4:00 PM - 5:30 PM**: Mentor Round 1 - Demo tasks 2.3, 3.1, 4.2 (Basic query/response)
- **5:30 PM - 9:00 PM**: Tasks 3, 4, 7, 9, 10 (Core features)
- **10:00 PM - 1:30 AM**: Tasks 11, 13, 14 (Integration and dashboard)
- **1:30 AM - 3:30 AM**: Mentor Round 2 - Full demo, tasks 15, 16 (Polish and error handling)
- **4:00 AM - 9:00 AM**: Tasks 17, 18, 20 (Deployment and final polish)
- **9:00 AM - 10:30 AM**: Task 20.4, final testing (Pitch rehearsal)
