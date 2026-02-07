# Requirements Document: Orbital Nexus MVP

## Introduction

Orbital Nexus is a micro-SaaS platform for guided farming that fuses public multi-satellite data (Sentinel, Landsat, ISRO) with soil, weather, and market datasets to provide Indian farmers with AI-driven crop recommendations and price predictions. The system addresses supply-demand imbalances in Indian agriculture (e.g., potato overproduction causing price crashes) by analyzing location-specific factors and historical trends to recommend optimal crops while promoting soil sustainability through rotation planning.

This MVP is built for the Hyperspace Innovation Hackathon 2026 (36-hour timeline) with emphasis on visual impact, ethical public data use, and demo stability for judging.

## Glossary

- **System**: The Orbital Nexus web application (frontend SPA + backend API)
- **User**: Indian farmer or agricultural stakeholder accessing the platform
- **Query**: Natural language input from user requesting crop guidance or analysis
- **AOI**: Area of Interest - user's geographic location (district-level precision)
- **Crop_Recommendation**: AI-generated suggestion for optimal crops based on fused data
- **Dashboard**: Generative UI sidebar displaying graphs, charts, and insights
- **Map_Visualization**: 2D Leaflet map showing location-based overlays (NDVI, fertility)
- **Fused_Data**: Combined dataset from satellite imagery, soil factors, weather, and mandi prices
- **NDVI**: Normalized Difference Vegetation Index from satellite data indicating land fertility
- **Mandi_Price**: Historical wholesale market prices for crops from Indian mandis
- **Rotation_Plan**: Seasonal crop sequence recommendation to maintain soil fertility
- **Freemium_Model**: Business model with free basic features and premium paid features

## Requirements

### Requirement 1: User Location Detection

**User Story:** As a farmer, I want the system to detect my location automatically, so that I receive recommendations relevant to my geographic area without manual input.

#### Acceptance Criteria

1. WHEN a user first accesses the SPA, THE System SHALL attempt to detect location via browser geolocation API
2. IF geolocation is denied or unavailable, THEN THE System SHALL default to Greater Noida, Uttar Pradesh as the AOI
3. WHEN location is detected, THE System SHALL display the AOI on the Map_Visualization with district-level precision
4. THE System SHALL allow users to manually override detected location via a profile input form
5. WHEN location is changed, THE System SHALL update all data queries and visualizations to reflect the new AOI

### Requirement 2: Natural Language Query Interface

**User Story:** As a farmer, I want to ask questions in natural language about crops and farming, so that I can get guidance without learning technical terminology.

#### Acceptance Criteria

1. THE System SHALL display a ChatGPT-style prompt box at the bottom-center of the SPA
2. WHEN the prompt box is displayed, THE System SHALL show 3 query suggestions (e.g., "Best crop for wet soil?", "Potato price next season?", "Yearly rotation plan?")
3. WHEN a userts a query, THE System SHALL display a progress bar for 2-5 seconds while processing
4. THE System SHALL parse user queries to identify intent categories: crop suitability, price prediction, or rotation planning
5. WHEN a query is submitted, THE System SHALL generate a response within 5 seconds using Fused_Data

### Requirement 3: Multi-Source Data Fusion

**User Story:** As a system administrator, I want to fuse satellite, soil, weather, and market data offline, so that the system can provide comprehensive recommendations without external API dependencies.

#### Acceptance Criteria

1. THE System SHALL load satellite data (NDVI from Landsat, optical imagery from Sentinel) from local CSV files in the /data folder
2. THE System SHALL load soil factor data (type, humidity, sunlight, salt content) from Kaggle CSV files stored locally
3. THE System SHALL load historical Mandi_Price data from local CSV files covering at least 3 years of records
4. THE System SHALL load weather data (rainfall, temperature) from local CSV files
5. WHEN querying data, THE System SHALL join datasets by location (latitude/longitude matching) using Pandas
6. THE System SHALL filter Fused_Data by user's AOI to return location-specific results
7. THE System SHALL complete data fusion queries within 3 seconds for any AOI

### Requirement 4: AI Crop Recommendation Engine

**User Story:** As a farmer, I want AI-driven crop recommendations based on my soil, weather, and market conditions, so that I can maximize profits and avoid overproduction losses.

#### Acceptance Criteria

1. WHEN a user queries for crop recommendations, THE System SHALL analyze soil type (sandy/wet), humidity (0-100%), sunlight (hours/day), and salt content (low/high) from Fused_Data
2. THE System SHALL apply rule-based scoring (e.g., if humidity >60% and soil type is wet, increase rice score)
3. THE System SHALL consider historical Mandi_Price trends to identify high-demand crops
4. THE System SHALL return top 3 Crop_Recommendation results with confidence scores
5. WHEN displaying recommendations, THE System SHALL include reasons for each crop (e.g., "Rice: Suits wet soil, predicted price 25-30 INR/kg due to low last-year supply")
6. THE System SHALL include sustainability notes (e.g., "Rotate with legumes to maintain soil fertility")

### Requirement 5: Price Prediction Engine

**User Story:** As a farmer, I want to see predicted crop prices for next season, so that I can plan which crops will be most profitable and avoid market gluts.

#### Acceptance Criteria

1. WHEN a user queries for price predictions, THE System SHALL retrieve historical Mandi_Price data for the requested crop covering the last 3 years
2. THE System SHALL calculate a simple linear trend using NumPy to predict next-season prices
3. THE System SHALL express predictions as price ranges (e.g., "25-30 INR/kg") with percentage change from current prices
4. IF historical supply data indicates overproduction risk, THEN THE System SHALL flag potential price drops (e.g., "Potato: Risk of 15% price drop due to high yield forecast")
5. THE System SHALL display price trends as bar graphs in the Dashboard using Recharts or Tembo AI SDK

### Requirement 6: Generative UI Dashboard

**User Story:** As a farmer, I want to see visual insights (graphs, charts, lists) generated dynamically based on my queries, so that I can understand complex data easily.

#### Acceptance Criteria

1. THE System SHALL display a left sidebar Dashboard that updates based on user queries
2. WHEN price data is queried, THE System SHALL generate bar graphs showing price trends over years
3. WHEN soil data is queried, THE System SHALL generate pie charts showing soil composition factors
4. WHEN rotation plans are requested, THE System SHALL generate ordered lists (e.g., "Q1: Wheat, Q2: Rice, Q3: Legumes")
5. WHERE Tembo AI SDK is available, THE System SHALL use it for dynamic dashboard generation
6. WHERE Tembo AI SDK fails or is unavailable, THE System SHALL fallback to static React Recharts components
7. THE Dashboard SHALL update within 2 seconds of query completion

### Requirement 7: Map Visualization with Overlays

**User Story:** As a farmer, I want to see my location on a map with visual overlays showing land fertility and crop suitability, so that I can understand spatial patterns in my area.

#### Acceptance Criteria

1. THE System SHALL display a 2D Leaflet map in the center-right section of the SPA
2. WHEN a user's AOI is detected or set, THE System SHALL center the map on that location with appropriate zoom level
3. THE System SHALL display NDVI heatmap overlays indicating land fertility levels (green for high, yellow for medium, red for low)
4. WHEN crop recommendations are generated, THE System SHALL optionally display crop suitability zones as colored overlays
5. THE System SHALL render map overlays without requiring external raster tile APIs (use matplotlib for simple heatmap images)
6. THE Map_Visualization SHALL update within 3 seconds when AOI changes

### Requirement 8: Sustainability and Rotation Planning

**User Story:** As a farmer, I want seasonal crop rotation recommendations, so that I can maintain soil fertility and avoid nutrient depletion over time.

#### Acceptance Criteria

1. WHEN a user requests a rotation plan, THE System SHALL generate a seasonal sequence of crops (e.g., "Rabi: Wheat, Kharif: Rice, Zaid: Legumes")
2. THE System SHALL ensure rotation plans alternate between nutrient-depleting and nitrogen-fixing crops
3. THE System SHALL include sustainability tips with every Crop_Recommendation (e.g., "Rotate to avoid nutrient loss")
4. THE System SHALL display rotation plans as ordered lists in the Dashboard
5. THE System SHALL base rotation suggestions on soil type and historical crop performance in the user's AOI

### Requirement 9: Freemium Business Model Interface

**User Story:** As a product owner, I want to display freemium features with upgrade prompts, so that we can demonstrate the business model to judges and potential partners.

#### Acceptance Criteria

1. THE System SHALL provide free access to basic crop recommendations and soil analysis
2. THE System SHALL display a mock "Upgrade to Premium" button in the Dashboard
3. WHEN premium features are accessed (e.g., detailed geopolitics analysis, advanced market trends), THE System SHALL show a modal explaining premium benefits
4. THE System SHALL include mock partnership integrations (e.g., "Alert fertilizer distributors for soil needs") as premium features
5. THE System SHALL clearly label free vs. premium features in the UI with visual indicators

### Requirement 10: Performance and Offline Operation

**User Story:** As a farmer in rural areas with limited connectivity, I want the system to work offline with pre-loaded data, so that I can access recommendations without internet dependency.

#### Acceptance Criteria

1. THE System SHALL load all datasets from local CSV files stored in the /data folder (no external API calls)
2. THE System SHALL complete initial page load within 5 seconds on standard broadband connections
3. THE System SHALL complete query processing and response generation within 5 seconds for any query type
4. THE System SHALL store all datasets locally with total size under 500MB
5. THE System SHALL be responsive and functional on mobile devices (viewport width 320px minimum)

### Requirement 11: Ethical Data Use and Disclaimers

**User Story:** As a system administrator, I want to ensure all data sources are public and ethical, so that the system complies with hackathon rules and avoids classified information.

#### Acceptance Criteria

1. THE System SHALL use only public datasets (Sentinel, Landsat, ISRO Resourcesat, Kaggle CSVs, data.gov.in)
2. THE System SHALL display disclaimers stating that recommendations are guidance, not guaranteed predictions
3. THE System SHALL not store or transmit user personal data beyond browser session storage
4. THE System SHALL include data source attributions in the footer (e.g., "Data: Sentinel, Landsat, ISRO, Kaggle")
5. THE System SHALL use guidance language (e.g., "Consider growing rice") rather than absolute predictions (e.g., "You must grow rice")

### Requirement 12: Demo Stability for Judging

**User Story:** As a hackathon participant, I want the system to be stable and visually impressive during judging, so that we can demonstrate all features without crashes or errors.

#### Acceptance Criteria

1. THE System SHALL handle invalid or empty queries gracefully with user-friendly error messages
2. WHEN data is missing for a specific AOI, THE System SHALL display a message suggesting nearby locations with available data
3. THE System SHALL pre-compute sample results for Greater Noida (default AOI) to ensure instant demo responses
4. THE System SHALL log errors to browser console without displaying technical stack traces to users
5. THE System SHALL include a "Reset Demo" button that clears state and returns to default Greater Noida AOI
6. THE System SHALL maintain visual consistency (eco-theme: greens/blues) across all components with no broken layouts
