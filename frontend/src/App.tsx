import { useState, useEffect } from "react";
import LandingPage from "./pages/LandingPage";
import Dashboard from "./pages/Dashboard";
import AuthPage from "./pages/AuthPage";
import { getStoredUser, logout, type User } from "./utils/auth";
import { ThemeProvider } from "./context/ThemeContext";

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
  const [initialAuthMode, setInitialAuthMode] = useState<"login" | "signup">("login");

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

  const handleLaunch = (mode?: any) => {
    const targetMode = (mode === "signup" || mode === "login") ? mode : "signup";
    setInitialAuthMode(targetMode);
    setView("auth");
  };

  return (
    <ThemeProvider>
      {view === "landing" && <LandingPage onLaunch={handleLaunch} />}
      {view === "auth" && (
        <AuthPage
          onAuth={handleAuth}
          initialMode={initialAuthMode}
          onBack={() => setView("landing")}
        />
      )}
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
