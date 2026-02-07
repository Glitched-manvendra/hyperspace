# Project Context: Orbital Nexus

## High-Level Vision

Orbital Nexus empowers Indian farmers with AI-driven insights for "guided farming" by fusing multi-source public datasets. The platform addresses the critical problem of crop supply-demand mismatches that cause devastating losses for 140M+ farmers (e.g., potato overproduction leading to 50% price crashes, or shortages driving unaffordable costs).

The system acts as a "startup advisor for farmers" - analyzing location-specific factors (soil type, humidity, sunlight, weather, satellite imagery) combined with historical market trends to recommend optimal crops, predict prices, and suggest sustainable rotation plans.

## Core Problem Being Solved

**Problem**: Indian farmers face volatile markets due to:
- Siloed data: Soil, weather, satellite, and market data exist separately
- Information asymmetry: Small farmers lack access to insights large agribusinesses have
- Overproduction cycles: Lack of coordination leads to gluts (e.g., potatoes flooding markets)
- Soil degradation: Continuous monoculture depletes nutrients

**Solution**: Orbital Nexus fuses satellite data (NDVI for fertility, optical imagery for land use) with soil factors, weather patterns, and historical mandi prices to provide:
1. Crop recommendations based on location-specific conditions
2. Price predictions to avoid overproduction/shortage cycles
3. Rotation plans to maintain soil fertility and sustainability

**Impact**: 20-30% yield improvement, reduced waste, sustainable farming practices

## Supported Query Types

The system handles three primary query categories:

### 1. Crop Suitability Guidance
- "What crop should I grow in wet soil?"
- "Best crop for Greater Noida next season?"
- "Which crops suit high humidity areas?"

**Output**: Top 3 crop recommendations with reasons, confidence scores, price ranges, and sustainability notes

### 2. Vegetation / Land Health
- "Show me land fertility in my area"
- "What is the NDVI for Greater Noida?"
- "Is my soil suitable for rice?"

**Output**: NDVI heatmap overlays on map, soil composition charts, land suitability analysis

### 3. Environmental Risk Awareness
- "What is the price trend for potatoes?"
- "Will rice prices increase next season?"
- "Is there overproduction risk for wheat?"

**Output**: Price trend graphs, predictions with percentage changes, overproduction risk flags

## What This Project Does NOT Do

**Explicitly out of scope**:

1. **No Real-Time Sensing**: System uses pre-loaded historical data, not live satellite feeds or IoT sensors
2. **No Guaranteed Predictions**: All outputs are guidance, not financial advice or guaranteed outcomes
3. **No Military Use**: Civilian agricultural application only, no defense or surveillance capabilities
4. **No Personal Data Collection**: No user authentication, no data storage beyond browser session
5. **No External API Dependencies**: Fully offline-capable, no real-time mandi price APIs (uses historical data)
6. **No Payment Processing**: Freemium model is mocked for demo, no actual payment integration
7. **No Machine Learning**: Uses simple rule-based AI and linear regression for hackathon speed
8. **No Multi-Language Support**: English only for MVP (Hindi support post-hackathon)

## Ethical Boundaries

- **Public Data Only**: Sentinel, Landsat, ISRO Resourcesat, Kaggle CSVs, data.gov.in
- **Guidance Language**: "Consider growing rice" not "You must grow rice"
- **Disclaimers**: Clear statements that recommendations are guidance, not guarantees
- **Privacy**: No user tracking, no data transmission to third parties
- **Sustainability Focus**: Promotes crop rotation, soil health, environmental responsibility
- **No Classified Information**: Avoids any ISRO/DRDO sensitive or restricted data

## Technical Philosophy

- **Demo-Ready Over Perfect**: Working prototype beats incomplete perfection
- **Visual Impact**: Maps, graphs, charts for judge appeal
- **Offline-First**: Pre-loaded data, no external dependencies
- **Simple AI**: Rule-based scoring, linear regression (not deep learning)
- **Graceful Degradation**: Fallbacks for every failure point
- **Mobile-Responsive**: Farmers access via phones

## Success Definition

A successful demo shows:
1. User enters query → System responds within 5 seconds
2. Dashboard generates relevant visualizations (graphs, charts, lists)
3. Map updates with location-specific overlays
4. Error handling works gracefully (no crashes)
5. Judges understand the farmer empowerment story
6. Visual design is polished and professional
