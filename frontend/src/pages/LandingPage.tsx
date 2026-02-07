import { motion } from "framer-motion";
import {
  Satellite,
  Sprout,
  TrendingDown,
  Database,
  Leaf,
  MapPin,
  BrainCircuit,
  BadgeCheck,
  WifiOff,
  HeartHandshake,
  ArrowRight,
  ChevronDown,
  Rocket,
} from "lucide-react";

/* ─── animation presets ─── */
const fadeUp = {
  hidden: { opacity: 0, y: 32 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.12, duration: 0.55, ease: "easeOut" },
  }),
};

const stagger = {
  visible: { transition: { staggerChildren: 0.12 } },
};

/* ─── types ─── */
interface LandingPageProps {
  onLaunch: () => void;
}

/* ═══════════════════════════════════════════════════════════════════
   LANDING PAGE
   ═══════════════════════════════════════════════════════════════════ */
export default function LandingPage({ onLaunch }: LandingPageProps) {
  return (
    <div className="min-h-screen bg-nexus-dark text-gray-100 overflow-x-hidden">
      {/* ────── NAV ────── */}
      <Nav onLaunch={onLaunch} />

      {/* ────── HERO ────── */}
      <HeroSection onLaunch={onLaunch} />

      {/* ────── PROBLEM ────── */}
      <ProblemSection />

      {/* ────── SOLUTION ────── */}
      <SolutionSection />

      {/* ────── TRUST ────── */}
      <TrustSection />

      {/* ────── CTA BAND ────── */}
      <CtaBand onLaunch={onLaunch} />

      {/* ────── FOOTER ────── */}
      <Footer />
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   NAV
   ═══════════════════════════════════════════════════════════════════ */
function Nav({ onLaunch }: { onLaunch: () => void }) {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-nexus-dark/70 border-b border-white/5">
      <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-cyan-400 grid place-items-center">
            <Satellite className="w-4 h-4 text-white" />
          </div>
          <span className="text-base font-semibold tracking-tight">
            Orbital Nexus
          </span>
        </div>

        <div className="hidden sm:flex items-center gap-8 text-sm text-gray-400">
          <a href="#problem" className="hover:text-white transition">Problem</a>
          <a href="#solution" className="hover:text-white transition">Solution</a>
          <a href="#trust" className="hover:text-white transition">Trust</a>
        </div>

        <button
          onClick={onLaunch}
          className="text-sm font-medium px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 transition-colors"
        >
          Launch Dashboard
        </button>
      </div>
    </nav>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   HERO
   ═══════════════════════════════════════════════════════════════════ */
function HeroSection({ onLaunch }: { onLaunch: () => void }) {
  return (
    <section className="relative min-h-screen flex items-center justify-center px-6 pt-20 overflow-hidden">
      {/* background grid + glow */}
      <div className="pointer-events-none absolute inset-0">
        {/* grid lines */}
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage:
              "linear-gradient(to right, #fff 1px, transparent 1px), linear-gradient(to bottom, #fff 1px, transparent 1px)",
            backgroundSize: "64px 64px",
          }}
        />
        {/* radial glow — emerald */}
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full bg-emerald-500/10 blur-[160px]" />
        {/* radial glow — blue */}
        <div className="absolute bottom-0 right-0 w-[500px] h-[500px] rounded-full bg-blue-500/8 blur-[120px]" />
      </div>

      {/* orbiting dots (decorative SVG) */}
      <OrbitDecoration />

      <motion.div
        initial="hidden"
        animate="visible"
        variants={stagger}
        className="relative z-10 max-w-3xl text-center flex flex-col items-center gap-6"
      >
        <motion.span
          variants={fadeUp}
          custom={0}
          className="inline-flex items-center gap-2 text-xs font-medium tracking-widest uppercase text-emerald-400 bg-emerald-400/10 rounded-full px-4 py-1.5 border border-emerald-400/20"
        >
          <Satellite className="w-3.5 h-3.5" />
          Hyperspace Innovation Hackathon 2026
        </motion.span>

        <motion.h1
          variants={fadeUp}
          custom={1}
          className="text-4xl sm:text-5xl md:text-6xl font-bold leading-tight tracking-tight"
        >
          Farming Guided by{" "}
          <span className="bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400 bg-clip-text text-transparent">
            Space Intelligence.
          </span>
        </motion.h1>

        <motion.p
          variants={fadeUp}
          custom={2}
          className="text-base sm:text-lg text-gray-400 max-w-xl leading-relaxed"
        >
          Fuse ISRO &amp; Sentinel satellite data with market trends to predict
          prices, optimize crops, and prevent market crashes — all offline.
        </motion.p>

        <motion.div
          variants={fadeUp}
          custom={3}
          className="flex flex-col sm:flex-row gap-3 mt-2"
        >
          <button
            onClick={onLaunch}
            className="group inline-flex items-center gap-2 px-7 py-3.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 font-semibold text-sm transition-all shadow-lg shadow-emerald-600/20"
          >
            <Rocket className="w-4 h-4" />
            Launch Orbital Nexus
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
          <a
            href="#problem"
            className="inline-flex items-center gap-2 px-7 py-3.5 rounded-xl border border-gray-700 text-gray-300 hover:border-gray-500 hover:text-white font-medium text-sm transition-colors"
          >
            Learn More
            <ChevronDown className="w-4 h-4" />
          </a>
        </motion.div>

        {/* stat chips */}
        <motion.div
          variants={fadeUp}
          custom={4}
          className="flex flex-wrap justify-center gap-4 mt-6 text-xs text-gray-500"
        >
          {["4 Satellite Sources", "100% Offline", "Real-time Fusion"].map(
            (t) => (
              <span
                key={t}
                className="flex items-center gap-1.5 bg-white/5 rounded-full px-3 py-1 border border-white/5"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                {t}
              </span>
            )
          )}
        </motion.div>
      </motion.div>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   PROBLEM
   ═══════════════════════════════════════════════════════════════════ */
function ProblemSection() {
  const cards = [
    {
      icon: TrendingDown,
      color: "text-red-400 bg-red-400/10 border-red-400/20",
      title: "Market Volatility",
      body: "In 2024, potato prices crashed 70% in UP — farmers lost ₹15,000/tonne because nobody predicted oversupply. Without fused data, markets are a gamble.",
    },
    {
      icon: Database,
      color: "text-amber-400 bg-amber-400/10 border-amber-400/20",
      title: "Siloed Data",
      body: "Weather data lives in one portal, soil health in another, market prices in a third. Farmers can't cross-reference — they make decisions blind.",
    },
    {
      icon: Leaf,
      color: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20",
      title: "Soil Degradation",
      body: "Repeated mono-cropping depletes nutrients. Without satellite NDVI trends + soil moisture fusion, degradation goes unnoticed until yields collapse.",
    },
  ];

  return (
    <section
      id="problem"
      className="relative py-24 sm:py-32 px-6"
    >
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.3 }}
          variants={stagger}
          className="text-center mb-14"
        >
          <motion.span
            variants={fadeUp}
            custom={0}
            className="text-xs font-semibold uppercase tracking-widest text-red-400"
          >
            The Problem
          </motion.span>
          <motion.h2
            variants={fadeUp}
            custom={1}
            className="text-3xl sm:text-4xl font-bold mt-3"
          >
            Why Indian Farmers Keep Losing
          </motion.h2>
          <motion.p
            variants={fadeUp}
            custom={2}
            className="text-gray-400 mt-3 max-w-lg mx-auto"
          >
            Every year, ₹90,000 crore is lost to market mispricing, data
            fragmentation, and avoidable soil damage.
          </motion.p>
        </motion.div>

        {/* Bento grid */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={stagger}
          className="grid grid-cols-1 md:grid-cols-3 gap-5"
        >
          {cards.map((c, i) => (
            <motion.div
              key={c.title}
              variants={fadeUp}
              custom={i}
              className="group relative rounded-2xl bg-white/[0.03] border border-white/[0.06] p-7 hover:border-white/10 transition-colors"
            >
              <div
                className={`w-11 h-11 rounded-xl ${c.color} border grid place-items-center mb-5`}
              >
                <c.icon className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-semibold mb-2">{c.title}</h3>
              <p className="text-sm text-gray-400 leading-relaxed">{c.body}</p>

              {/* subtle hover glow */}
              <div className="pointer-events-none absolute -inset-px rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity bg-gradient-to-br from-white/[0.02] to-transparent" />
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   SOLUTION  — 3-step horizontal flow
   ═══════════════════════════════════════════════════════════════════ */
function SolutionSection() {
  const steps = [
    {
      num: "01",
      icon: MapPin,
      color: "from-emerald-500 to-teal-500",
      title: "Select Your Land",
      body: "Pinpoint your farmland on an interactive satellite map. We auto-detect district, soil type, and recent crop history.",
    },
    {
      num: "02",
      icon: BrainCircuit,
      color: "from-cyan-500 to-blue-500",
      title: "AI Fuses Satellite Data",
      body: "We cross-correlate ISRO weather, Sentinel NDVI, NASA soil moisture, and mandi prices — in seconds, fully offline.",
    },
    {
      num: "03",
      icon: Sprout,
      color: "from-teal-500 to-emerald-500",
      title: "Get Profitable Guidance",
      body: "Receive crop recommendations, price predictions, and soil health alerts — all in plain Hindi or English.",
    },
  ];

  return (
    <section
      id="solution"
      className="relative py-24 sm:py-32 px-6 bg-gradient-to-b from-transparent via-emerald-950/10 to-transparent"
    >
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.3 }}
          variants={stagger}
          className="text-center mb-16"
        >
          <motion.span
            variants={fadeUp}
            custom={0}
            className="text-xs font-semibold uppercase tracking-widest text-emerald-400"
          >
            How It Works
          </motion.span>
          <motion.h2
            variants={fadeUp}
            custom={1}
            className="text-3xl sm:text-4xl font-bold mt-3"
          >
            From Satellite to Farm — in 3 Steps
          </motion.h2>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={stagger}
          className="grid grid-cols-1 md:grid-cols-3 gap-8"
        >
          {steps.map((s, i) => (
            <motion.div
              key={s.num}
              variants={fadeUp}
              custom={i}
              className="relative flex flex-col items-center text-center"
            >
              {/* connector line (hidden on mobile) */}
              {i < steps.length - 1 && (
                <div className="hidden md:block absolute top-12 left-[60%] w-[80%] h-px bg-gradient-to-r from-white/10 to-transparent" />
              )}

              <div
                className={`w-20 h-20 rounded-2xl bg-gradient-to-br ${s.color} grid place-items-center shadow-lg shadow-emerald-600/10 mb-5`}
              >
                <s.icon className="w-8 h-8 text-white" />
              </div>

              <span className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">
                Step {s.num}
              </span>
              <h3 className="text-lg font-semibold mb-2">{s.title}</h3>
              <p className="text-sm text-gray-400 max-w-xs leading-relaxed">
                {s.body}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   TRUST  — badges
   ═══════════════════════════════════════════════════════════════════ */
function TrustSection() {
  const badges = [
    {
      icon: BadgeCheck,
      label: "100% Public Data",
      desc: "ISRO, Sentinel-2, NASA SMAP, Open-Meteo — all open-access datasets.",
    },
    {
      icon: WifiOff,
      label: "Offline-First Architecture",
      desc: "Works without internet. All data is bundled. Ideal for rural India.",
    },
    {
      icon: HeartHandshake,
      label: "Sustainability Focused",
      desc: "Promotes crop rotation, soil health monitoring, and ecological balance.",
    },
  ];

  return (
    <section
      id="trust"
      className="relative py-24 sm:py-32 px-6"
    >
      <div className="max-w-5xl mx-auto">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.3 }}
          variants={stagger}
          className="text-center mb-14"
        >
          <motion.span
            variants={fadeUp}
            custom={0}
            className="text-xs font-semibold uppercase tracking-widest text-cyan-400"
          >
            Trust & Impact
          </motion.span>
          <motion.h2
            variants={fadeUp}
            custom={1}
            className="text-3xl sm:text-4xl font-bold mt-3"
          >
            Built on Transparency
          </motion.h2>
          <motion.p
            variants={fadeUp}
            custom={2}
            className="text-gray-400 mt-3 max-w-md mx-auto"
          >
            Built for Hyperspace Innovation Hackathon 2026 — designed to be
            auditable, accessible, and impactful.
          </motion.p>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={stagger}
          className="grid grid-cols-1 sm:grid-cols-3 gap-6"
        >
          {badges.map((b, i) => (
            <motion.div
              key={b.label}
              variants={fadeUp}
              custom={i}
              className="flex flex-col items-center text-center rounded-2xl border border-white/[0.06] bg-white/[0.02] p-8 hover:border-cyan-500/20 transition-colors"
            >
              <div className="w-12 h-12 rounded-full bg-cyan-400/10 border border-cyan-400/20 grid place-items-center mb-4">
                <b.icon className="w-5 h-5 text-cyan-400" />
              </div>
              <h3 className="font-semibold mb-1">{b.label}</h3>
              <p className="text-sm text-gray-500 leading-relaxed">{b.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   CTA BAND
   ═══════════════════════════════════════════════════════════════════ */
function CtaBand({ onLaunch }: { onLaunch: () => void }) {
  return (
    <section className="py-20 px-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.97 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
        className="max-w-4xl mx-auto relative rounded-3xl overflow-hidden"
      >
        {/* bg gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-600/20 via-teal-600/10 to-cyan-600/20 border border-white/[0.08] rounded-3xl" />

        <div className="relative z-10 flex flex-col items-center text-center py-16 px-8">
          <h2 className="text-2xl sm:text-3xl font-bold mb-3">
            Ready to farm smarter?
          </h2>
          <p className="text-gray-400 mb-8 max-w-md">
            Enter the dashboard, type a question in plain language, and get
            satellite-backed answers in seconds.
          </p>
          <button
            onClick={onLaunch}
            className="group inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-white text-nexus-dark font-semibold text-sm hover:bg-gray-100 transition-colors shadow-xl shadow-black/20"
          >
            <Rocket className="w-4 h-4" />
            Open Orbital Nexus
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </motion.div>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   FOOTER
   ═══════════════════════════════════════════════════════════════════ */
function Footer() {
  return (
    <footer className="border-t border-white/5 py-10 px-6">
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-gray-500">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-full bg-gradient-to-br from-emerald-500 to-cyan-400 grid place-items-center">
            <Satellite className="w-3 h-3 text-white" />
          </div>
          <span className="font-medium text-gray-400">Orbital Nexus</span>
        </div>

        <p>Built with ❤️ in Ghaziabad · Hyperspace 2026</p>

        <div className="flex gap-5 text-gray-600">
          <a href="#problem" className="hover:text-gray-300 transition">Problem</a>
          <a href="#solution" className="hover:text-gray-300 transition">Solution</a>
          <a href="#trust" className="hover:text-gray-300 transition">Trust</a>
        </div>
      </div>
    </footer>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   ORBIT DECORATION  — light SVG rings behind hero
   ═══════════════════════════════════════════════════════════════════ */
function OrbitDecoration() {
  return (
    <div className="pointer-events-none absolute inset-0 flex items-center justify-center opacity-[0.07]">
      <svg
        width="720"
        height="720"
        viewBox="0 0 720 720"
        fill="none"
        className="animate-[spin_90s_linear_infinite]"
      >
        <circle cx="360" cy="360" r="200" stroke="white" strokeWidth="0.5" />
        <circle cx="360" cy="360" r="280" stroke="white" strokeWidth="0.5" />
        <circle cx="360" cy="360" r="350" stroke="white" strokeWidth="0.5" />
        {/* orbiting dots */}
        <circle cx="560" cy="360" r="4" fill="#34d399" />
        <circle cx="360" cy="80" r="3" fill="#22d3ee" />
        <circle cx="160" cy="500" r="3.5" fill="#60a5fa" />
      </svg>
    </div>
  );
}
