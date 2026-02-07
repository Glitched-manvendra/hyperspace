import { useState, type FormEvent } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Phone,
  Lock,
  User,
  MapPin,
  ArrowRight,
  Loader2,
  Satellite,
  Sprout,
  Eye,
  EyeOff,
} from "lucide-react";

import { signup, login } from "../utils/auth";

interface AuthPageProps {
  onAuth: (user: { phone: string; name: string; village: string }) => void;
}

/* ─── animation presets ─── */
const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } },
};

const stagger = {
  visible: { transition: { staggerChildren: 0.08 } },
};

/**
 * AuthPage — Phone + Password login/signup (Space-Glass aesthetic)
 *
 * Self-contained auth for farmers. No external dependencies.
 * Stores sessions via JWT tokens in localStorage.
 */
export default function AuthPage({ onAuth }: AuthPageProps) {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [village, setVillage] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (mode === "signup") {
        const user = await signup(phone, password, name, village);
        onAuth(user);
      } else {
        const user = await login(phone, password);
        onAuth(user);
      }
    } catch (err: unknown) {
      if (err && typeof err === "object" && "response" in err) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        setError(axiosErr.response?.data?.detail ?? "Authentication failed");
      } else {
        setError("Cannot connect to server. Is the backend running?");
      }
    } finally {
      setLoading(false);
    }
  };

  const isValid =
    phone.length >= 10 &&
    password.length >= 4 &&
    (mode === "login" || name.trim().length > 0);

  return (
    <div className="min-h-screen bg-bg text-text flex items-center justify-center relative overflow-hidden">
      {/* ── Ambient blobs ── */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-[-15%] left-[-10%] w-[600px] h-[600px] bg-primary/15 rounded-full blur-[160px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[700px] h-[700px] bg-accent/15 rounded-full blur-[180px]" />
        <div className="absolute top-[60%] left-[60%] w-[300px] h-[300px] bg-blue-500/10 rounded-full blur-[120px]" />
      </div>

      {/* ── Floating orbit decoration ── */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] pointer-events-none z-0 opacity-20">
        <div className="absolute inset-0 border border-primary/20 rounded-full animate-[spin_60s_linear_infinite]" />
        <div className="absolute inset-6 border border-accent/15 rounded-full animate-[spin_45s_linear_infinite_reverse]" />
        <div className="absolute inset-12 border border-blue-500/10 rounded-full animate-[spin_30s_linear_infinite]" />
      </div>

      <motion.div
        initial="hidden"
        animate="visible"
        variants={stagger}
        className="relative z-10 w-full max-w-md px-4"
      >
        {/* ── Logo + branding ── */}
        <motion.div variants={fadeUp} className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl overflow-hidden shadow-lg shadow-primary/20">
              <img src="/logo.png" alt="Orbital Nexus" className="w-full h-full object-cover" />
            </div>
            <div className="text-left">
              <h1 className="text-xl font-display font-bold text-white tracking-tight">
                Orbital Nexus
              </h1>
              <p className="text-[10px] text-sage uppercase tracking-[0.2em]">
                Satellite-Powered Farming
              </p>
            </div>
          </div>
        </motion.div>

        {/* ── Auth card ── */}
        <motion.div
          variants={fadeUp}
          className="neo-box p-8"
        >
          {/* Mode tabs */}
          <div className="flex gap-2 mb-6">
            <button
              onClick={() => { setMode("login"); setError(null); }}
              className={`flex-1 py-2.5 font-bold border-2 border-border transition-all ${
                mode === "login"
                  ? "bg-primary text-black shadow-neo-sm"
                  : "bg-surface text-text hover:bg-bg"
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => { setMode("signup"); setError(null); }}
              className={`flex-1 py-2.5 font-bold border-2 border-border transition-all ${
                mode === "signup"
                  ? "bg-primary text-black shadow-neo-sm"
                  : "bg-surface text-text hover:bg-bg"
              }`}
            >
              Register
            </button>
          </div>

          {/* Title */}
          <AnimatePresence mode="wait">
            <motion.div
              key={mode}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className="mb-6"
            >
              <h2 className="text-xl font-display font-bold text-text">
                {mode === "login" ? "Welcome Back" : "Join Orbital Nexus"}
              </h2>
              <p className="text-xs text-text/70 mt-1 font-mono">
                {mode === "login"
                  ? "Sign in to access satellite insights"
                  : "Create account for crop predictions"}
              </p>
            </motion.div>
          </AnimatePresence>

          {/* Error */}
          {error && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 mb-4"
            >
              <p className="text-xs text-red-400">{error}</p>
            </motion.div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name (signup only) */}
            <AnimatePresence>
              {mode === "signup" && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <label className="block text-[11px] text-sage uppercase tracking-wider font-medium mb-1.5">
                    Full Name
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text/50" />
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="e.g., Rajesh Kumar"
                      className="neo-input pl-10"
                    />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Phone */}
            <div>
              <label className="block text-[11px] text-sage uppercase tracking-wider font-medium mb-1.5">
                Mobile Number
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text/50" />
                <span className="absolute left-9 top-1/2 -translate-y-1/2 text-sm text-text/60 font-mono">
                  +91
                </span>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value.replace(/\D/g, "").slice(0, 10))}
                  placeholder="9876543210"
                  className="neo-input pl-[4.5rem]"
                  maxLength={10}
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-[11px] text-sage uppercase tracking-wider font-medium mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text/50" />
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Min 4 characters"
                  className="neo-input pl-10 pr-12"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-sage/50 hover:text-white transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Village (signup only) */}
            <AnimatePresence>
              {mode === "signup" && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <label className="block text-[11px] text-sage uppercase tracking-wider font-medium mb-1.5">
                    Village / City <span className="text-sage/30">(optional)</span>
                  </label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text/50" />
                    <input
                      type="text"
                      value={village}
                      onChange={(e) => setVillage(e.target.value)}
                      placeholder="e.g., Pune"
                      className="neo-input pl-10"
                    />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading || !isValid}
              className="neo-button w-full justify-center bg-primary text-black font-bold py-3.5 text-sm disabled:opacity-50 disabled:shadow-none"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  {mode === "login" ? "Signing In…" : "Creating Account…"}
                </>
              ) : (
                <>
                  {mode === "login" ? "Sign In" : "Create Farmer Account"}
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        </motion.div>

        {/* ── Bottom features row ── */}
        <motion.div
          variants={fadeUp}
          className="flex items-center justify-center gap-6 mt-6 text-[10px] text-sage/60"
        >
          <span className="flex items-center gap-1.5">
            <Satellite className="w-3 h-3" />
            4+ Satellite Sources
          </span>
          <span className="flex items-center gap-1.5">
            <Sprout className="w-3 h-3" />
            AI Crop Brain
          </span>
          <span className="flex items-center gap-1.5">
            <Lock className="w-3 h-3" />
            Offline-Ready
          </span>
        </motion.div>

        {/* ── Skip for demo ── */}
        <motion.div variants={fadeUp} className="text-center mt-4">
          <button
            onClick={() => onAuth({ phone: "demo", name: "Demo Farmer", village: "India" })}
            className="text-xs text-sage/40 hover:text-sage transition-colors underline underline-offset-2"
          >
            Skip login (demo mode)
          </button>
        </motion.div>
      </motion.div>
    </div>
  );
}
