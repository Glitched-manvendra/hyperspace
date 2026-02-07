# Project Constraints: Orbital Nexus

## Non-Negotiable Rules

### Data Constraints

1. **Offline Datasets Only**
   - All data must be pre-loaded in /data folder as CSV files
   - No external API calls during query processing
   - No real-time satellite data fetching
   - No live mandi price APIs (use historical data only)
   - Exception: OpenStreetMap tiles for base map (standard, no API key)

2. **Public Data Only**
   - Sentinel (ESA): Public satellite imagery
   - Landsat (NASA/USGS): Public NDVI and land use data
   - ISRO Resourcesat: Public agricultural monitoring data
   - Kaggle datasets: Public soil, weather, crop, and price CSVs
   - data.gov.in: Public government datasets
   - No classified, restricted, or proprietary data sources

3. **Data Size Limit**
   - Total dataset size: <500MB
   - Individual CSV files: <100MB each
   - Optimize by filtering to relevant regions (focus on Uttar Pradesh)

### Feature Constraints

4. **No New Features Without Explicit Instruction**
   - Stick to requirements document scope
   - Do not add "nice to have" features during hackathon
   - Focus on core: query → recommendation → visualization
   - Defer enhancements to post-hackathon phase

5. **Prefer Clarity Over Cleverness**
   - Simple rule-based AI over complex ML models
   - Linear regression over neural networks
   - Readable code over optimized but obscure code
   - Comments explaining intent, not implementation

6. **Visual Demo > Algorithmic Depth**
   - Working map with overlays beats perfect NDVI calculation
   - Dashboard with graphs beats optimal recommendation algorithm
   - Smooth animations beat millisecond performance gains
   - Judge comprehension beats technical sophistication

7. **Use Guidance Language, Not Predictions**
   - "Consider growing rice" not "Grow rice"
   - "May increase by 15%" not "Will increase by 15%"
   - "Suggested rotation plan" not "Required rotation plan"
   - "Based on historical trends" not "Guaranteed outcome"

### Hackathon Constraints

8. **36-Hour Timeline**
   - Prioritize tasks for Mentor Round 1 (4:00 PM Day 1)
   - Full demo ready by Mentor Round 2 (1:30 AM Day 2)
   - Final polish by judging (10:30 AM Day 2)
   - No time for refactoring or optimization

9. **Demo Stability**
   - Pre-compute results for Greater Noida (default location)
   - Cache sample queries for instant responses
   - Error boundaries on all components
   - Graceful fallbacks for every failure point
   - Test on mobile devices before judging

10. **Judge Comprehension**
    - Clear visual hierarchy (logo, map, dashboard, prompt)
    - Intuitive interactions (click suggestions, see results)
    - Obvious value proposition (farmer empowerment)
    - Professional design (eco-theme: greens/blues)
    - No technical jargon in UI

### Technical Constraints

11. **Technology Stack**
    - Frontend: React 19, TypeScript, TailwindCSS, Leaflet, Recharts
    - Backend: Python 3.12, FastAPI, Pandas, NumPy
    - No database (CSV files only)
    - No authentication (open access for demo)
    - No payment processing (mock freemium model)

12. **Performance Requirements**
    - Query processing: <5 seconds
    - Dashboard update: <2 seconds
    - Map overlay update: <3 seconds
    - Initial page load: <5 seconds
    - Mobile responsive: 320px minimum width

13. **Browser Compatibility**
    - Target: Chrome, Firefox, Safari (latest versions)
    - Mobile: iOS Safari, Chrome Android
    - No IE11 support required

### Ethical Constraints

14. **Privacy**
    - No user authentication or accounts
    - No data storage beyond browser session
    - No tracking or analytics (for hackathon)
    - No data transmission to third parties

15. **Disclaimers**
    - Display disclaimer on landing page and SPA
    - State recommendations are guidance, not guarantees
    - Attribute all data sources in footer
    - Use guidance language throughout

16. **Sustainability Focus**
    - Promote crop rotation for soil health
    - Highlight environmental benefits
    - Avoid recommendations that harm soil fertility
    - Include sustainability notes with every recommendation

### Deployment Constraints

17. **Hosting**
    - Primary: Hostinger (orbitalnexus.online)
    - Fallback: Vercel/Netlify (frontend), Railway/Render (backend)
    - No AWS/GCP/Azure (cost and complexity)

18. **Environment Variables**
    - No secrets in code (use .env files)
    - .env files in .gitignore
    - Document all required environment variables

### Code Quality Constraints

19. **Testing**
    - Property tests for core correctness properties
    - Unit tests for critical paths
    - Manual testing for UI/UX
    - No time for comprehensive test coverage (aim for 80%)

20. **Documentation**
    - README with setup instructions
    - Code comments for complex logic
    - API documentation (FastAPI auto-generates)
    - No time for extensive documentation

### Team Constraints

21. **Parallel Work**
    - Frontend and backend developed simultaneously
    - Clear API contract defined upfront
    - Mock data for frontend development
    - Integration testing before Mentor Round 2

22. **Communication**
    - Use Git for version control
    - Clear commit messages
    - Coordinate via team chat
    - Ask for help when blocked (don't waste time)

## Constraint Violations

**If you encounter a constraint violation, STOP and ask the user before proceeding.**

Examples:
- "This feature requires a real-time API, which violates the offline constraint. Should we use cached data instead?"
- "This optimization would make the code harder to understand. Should we prioritize clarity?"
- "This dataset is not publicly available. Should we find an alternative source?"

## Constraint Priorities

When constraints conflict, prioritize in this order:
1. Demo stability (no crashes during judging)
2. Ethical compliance (public data, guidance language)
3. Visual impact (judge appeal)
4. Feature completeness (all core features working)
5. Code quality (readable, maintainable)
6. Performance (fast enough, not optimal)
