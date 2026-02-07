import { useState, useEffect } from "react";
import LandingPage from "./pages/LandingPage";
import Dashboard from "./pages/Dashboard";
import AuthPage from "./pages/AuthPage";
import { getStoredUser, logout, type User } from "./utils/auth";
import { ThemeProvider } from "./context/ThemeContext";
import { ThemeToggle } from "./components/ThemeToggle";

/**
 * Orbital Nexus — Root Application
 *
 * State-based navigation:
 *   "landing"   → Marketing / Landing page (Space-Glass)
 *   "auth"      → Phone + password login/signup
 *   "dashboard" → Main SPA (Map + Sidebar + Prompt)
 */
type View = "landing" | "auth" | "dashboard";

function App() {
  const [view, setView] = useState<View>("landing");
  const [user, setUser] = useState<User | null>(null);

  // Restore session on mount
  useEffect(() => {
    const stored = getStoredUser();
    if (stored) setUser(stored);
  }, []);

  const handleAuth = (u: User) => {
    setUser(u);
    setView("dashboard");
  };

  const handleLogout = () => {
    logout();
    setUser(null);
    setView("landing");
  };

  const handleLaunch = () => {
    if (user) {
      setView("dashboard");
    } else {
      setView("auth");
    }
  };

  return (
    <ThemeProvider>
      <ThemeToggle />
      {view === "landing" && <LandingPage onLaunch={handleLaunch} />}
      {view === "auth" && <AuthPage onAuth={handleAuth} />}
      {view === "dashboard" && (
        <Dashboard
          onBack={() => setView("landing")}
          user={user}
          onLogout={handleLogout}
        />
      )}
    </ThemeProvider>
  );
}

export default App;
