import { useState } from "react";
import LandingPage from "./pages/LandingPage";
import Dashboard from "./pages/Dashboard";

/**
 * Orbital Nexus — Root Application
 *
 * State-based navigation:
 *   "landing"   → Marketing / Landing page (Space-Glass)
 *   "dashboard" → Main SPA (Map + Sidebar + Prompt)
 */
type View = "landing" | "dashboard";

function App() {
  const [view, setView] = useState<View>("landing");

  if (view === "landing") {
    return <LandingPage onLaunch={() => setView("dashboard")} />;
  }

  return <Dashboard onBack={() => setView("landing")} />;
}

export default App;
