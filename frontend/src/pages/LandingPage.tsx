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
  Globe,
  Zap,
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
   LANDING PAGE — Space-Glass Aesthetic
   ═══════════════════════════════════════════════════════════════════ */
export default function LandingPage({ onLaunch }: LandingPageProps) {
  return (
    <div className="h-screen overflow-y-auto custom-scrollbar bg-bg text-text relative">
      {/* ── Global ambient blobs ── */}
      {/* ── Global ambient blobs (Hidden for Neo-Brutalism) ── */}
      {/* <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-[-15%] left-[-10%] w-[600px] h-[600px] bg-primary/15 rounded-full blur-[160px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[700px] h-[700px] bg-accent/15 rounded-full blur-[180px]" />
        <div className="absolute top-[40%] right-[20%] w-[300px] h-[300px] bg-blue-500/10 rounded-full blur-[120px]" />
      </div> */}

      {/* ── NAV ── */}
      <Nav onLaunch={onLaunch} />

      {/* ── HERO ── */}
      <HeroSection onLaunch={onLaunch} />

      {/* ── PROBLEM ── */}
      <ProblemSection />

      {/* ── SOLUTION ── */}
      <SolutionSection />

      {/* ── DATA SOURCES ── */}
      <DataSourcesSection />

      {/* ── TRUST ── */}
      <TrustSection />

      {/* ── CTA BAND ── */}
      <CtaBand onLaunch={onLaunch} />

      {/* ── FOOTER ── */}
      <Footer />
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   NAV — Glass navbar
   ═══════════════════════════════════════════════════════════════════ */
function Nav({ onLaunch }: { onLaunch: () => void }) {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-surface border-b-2 border-border shadow-neo-sm">
      <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-3">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg overflow-hidden">
            <img src="/logo.png" alt="Orbital Nexus" className="w-full h-full object-cover" />
          </div>
          <span className="text-base font-display font-bold tracking-tight">
            Orbital Nexus
          </span>
        </div>

        <div className="hidden sm:flex items-center gap-8 text-sm text-sage">
           <a href="#problem" className="hover:text-primary transition font-medium">Problem</a>
           <a href="#solution" className="hover:text-primary transition font-medium">Solution</a>
           <a href="#data" className="hover:text-primary transition font-medium">Data</a>
           <a href="#trust" className="hover:text-primary transition font-medium">Trust</a>
        </div>

        <button
          onClick={onLaunch}
          className="neo-button px-5 py-2 rounded-none text-sm font-bold bg-primary text-black hover:bg-primary/90"
        >
          Launch Dashboard
        </button>
      </div>
    </nav>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   HERO — Glass hero with orbit decoration
   ═══════════════════════════════════════════════════════════════════ */
function HeroSection({ onLaunch }: { onLaunch: () => void }) {
  return (
    <section className="relative min-h-screen flex items-center justify-center px-6 pt-20 overflow-hidden">
      {/* Grid overlay */}
      <div className="pointer-events-none absolute inset-0">
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage:
              "linear-gradient(to right, #fff 1px, transparent 1px), linear-gradient(to bottom, #fff 1px, transparent 1px)",
            backgroundSize: "72px 72px",
          }}
        />
      </div>

      <OrbitDecoration />

      <motion.div
        initial="hidden"
        animate="visible"
        variants={stagger}
        className="relative z-10 max-w-4xl text-center flex flex-col items-center gap-6"
      >
        <motion.div
           variants={fadeUp}
           custom={0}
           className="inline-flex items-center gap-2 px-4 py-2 bg-surface border-2 border-border shadow-neo-sm"
         >
           <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
           <span className="text-xs text-text uppercase tracking-wider font-bold">
             Hyperspace Innovation Hackathon 2026 — PS #4
           </span>
         </motion.div>

        <motion.h1
          variants={fadeUp}
          custom={1}
          className="text-5xl sm:text-6xl md:text-7xl font-display font-bold leading-tight"
        >
          Guided Farming with{" "}
           <span className="text-primary underline decoration-4 decoration-border">
             Satellite Intelligence
           </span>
         </motion.h1>

        <motion.p
          variants={fadeUp}
          custom={2}
          className="text-lg sm:text-xl text-sage max-w-2xl leading-relaxed"
        >
          Eliminate supply-demand imbalances. We fuse ISRO, Sentinel &amp; Landsat
          data with market trends to predict profitable crops for Indian farmers.
        </motion.p>

        <motion.div
          variants={fadeUp}
          custom={3}
          className="flex flex-col sm:flex-row gap-4 mt-4"
        >
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onLaunch}
            className="group relative px-8 py-4 bg-white text-black font-bold rounded-full text-lg shadow-[0_0_40px_rgba(255,255,255,0.2)] hover:shadow-[0_0_60px_rgba(255,255,255,0.35)] transition-shadow"
          >
            <span className="flex items-center gap-2">
              <Rocket className="w-5 h-5" />
              Analyze My Land
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </span>
          </motion.button>
          <a
             href="#problem"
             className="neo-button px-7 py-4 bg-surface text-text font-bold"
           >
             Learn More
             <ChevronDown className="w-4 h-4 ml-2 inline" />
           </a>
        </motion.div>

        {/* Stat chips */}
        <motion.div
          variants={fadeUp}
          custom={4}
          className="flex flex-wrap justify-center gap-4 mt-8 text-xs text-sage"
        >
          {[
            { label: "4 Satellite Sources", color: "bg-primary" },
            { label: "Open-Meteo Live", color: "bg-accent" },
            { label: "ISRO Bhuvan Verified", color: "bg-blue-400" },
            { label: "20 Districts Mapped", color: "bg-gold" },
          ].map((chip) => (
            <span
              key={chip.label}
              className="flex items-center gap-2 neo-box border-2 px-4 py-2"
            >
              <span className={`w-2 h-2 rounded-full ${chip.color}`} />
              {chip.label}
            </span>
          ))}
        </motion.div>
      </motion.div>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   PROBLEM — Glass bento grid
   ═══════════════════════════════════════════════════════════════════ */
function ProblemSection() {
  const cards = [
    {
      icon: TrendingDown,
      color: "text-red-400",
      glow: "from-red-500/20 to-transparent",
      title: "Market Volatility",
      body: "In 2024, potato prices crashed 70% in UP — farmers lost ₹15,000/tonne because nobody predicted oversupply.",
    },
    {
      icon: Database,
      color: "text-gold",
      glow: "from-amber-500/20 to-transparent",
      title: "Siloed Data",
      body: "Weather in one portal, soil in another, prices in a third. Farmers can't cross-reference — decisions are blind.",
    },
    {
      icon: Leaf,
      color: "text-primary",
      glow: "from-emerald-500/20 to-transparent",
      title: "Soil Degradation",
      body: "Mono-cropping depletes nutrients. Without NDVI + soil moisture fusion, degradation goes unnoticed until yields collapse.",
    },
  ];

  return (
    <section id="problem" className="relative py-28 px-6">
      <div className="max-w-6xl mx-auto relative z-10">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.3 }}
          variants={stagger}
          className="text-center mb-16"
        >
          <motion.span variants={fadeUp} custom={0} className="text-xs font-semibold uppercase tracking-widest text-red-400">
            The Problem
          </motion.span>
          <motion.h2 variants={fadeUp} custom={1} className="text-3xl sm:text-4xl font-display font-bold mt-3">
            Why Indian Farmers Keep Losing
          </motion.h2>
          <motion.p variants={fadeUp} custom={2} className="text-sage mt-3 max-w-lg mx-auto">
            Every year, ₹90,000 crore is lost to market mispricing, data fragmentation, and avoidable soil damage.
          </motion.p>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={stagger}
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          {cards.map((c, i) => (
            <motion.div
              key={c.title}
              variants={fadeUp}
              custom={i}
              className="group relative neo-box p-8"
            >
              <div className={`w-12 h-12 rounded-xl bg-white/5 border border-white/10 grid place-items-center mb-6 ${c.color}`}>
                <c.icon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-display font-bold mb-3">{c.title}</h3>
              <p className="text-sm text-sage leading-relaxed">{c.body}</p>
              {/* Hover glow */}
              <div className={`pointer-events-none absolute -inset-px rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity bg-gradient-to-br ${c.glow}`} />
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   SOLUTION — 3-step glass flow
   ═══════════════════════════════════════════════════════════════════ */
function SolutionSection() {
  const steps = [
    {
      num: "01",
      icon: MapPin,
      gradient: "from-primary to-teal-500",
      title: "Select Your Land",
      body: "Pinpoint your farmland on the satellite map. We auto-detect district, soil type, and recent crop history.",
    },
    {
      num: "02",
      icon: BrainCircuit,
      gradient: "from-accent to-blue-500",
      title: "AI Fuses Satellite Data",
      body: "Cross-correlate ISRO weather, Sentinel NDVI, NASA soil moisture, and mandi prices — in seconds.",
    },
    {
      num: "03",
      icon: Sprout,
      gradient: "from-teal-500 to-primary",
      title: "Get Profitable Guidance",
      body: "Crop recommendations, price predictions, and soil health alerts — plain Hindi or English.",
    },
  ];

  return (
    <section id="solution" className="relative py-28 px-6">
      {/* Section ambient */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/5 to-transparent pointer-events-none" />

      <div className="max-w-6xl mx-auto relative z-10">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.3 }}
          variants={stagger}
          className="text-center mb-16"
        >
          <motion.span variants={fadeUp} custom={0} className="text-xs font-semibold uppercase tracking-widest text-primary">
            How It Works
          </motion.span>
          <motion.h2 variants={fadeUp} custom={1} className="text-3xl sm:text-4xl font-display font-bold mt-3">
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
              {i < steps.length - 1 && (
                <div className="hidden md:block absolute top-14 left-[60%] w-[80%] h-px bg-gradient-to-r from-white/10 to-transparent" />
              )}

              <div className={`w-24 h-24 border-2 border-border grid place-items-center shadow-neo mb-6 bg-surface`}>
                <s.icon className={`w-10 h-10 ${s.gradient.includes("primary") ? "text-primary" : "text-accent"}`} />
              </div>

              <span className="text-xs font-bold text-sage uppercase tracking-widest mb-2">
                Step {s.num}
              </span>
              <h3 className="text-xl font-display font-bold mb-3">{s.title}</h3>
              <p className="text-sm text-sage max-w-xs leading-relaxed">{s.body}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   DATA SOURCES — Show real API integrations
   ═══════════════════════════════════════════════════════════════════ */
function DataSourcesSection() {
  const sources = [
    { icon: Globe, name: "Open-Meteo", desc: "Live weather, soil moisture", status: "Live API", color: "text-primary" },
    { icon: Satellite, name: "ISRO Bhuvan", desc: "LULC land classification", status: "Live API", color: "text-accent" },
    { icon: Zap, name: "Agromonitoring", desc: "Satellite imagery & NDVI", status: "Connected", color: "text-gold" },
    { icon: Database, name: "Soil Database", desc: "20 Indian districts mapped", status: "Offline", color: "text-blue-400" },
  ];

  return (
    <section id="data" className="relative py-28 px-6">
      <div className="max-w-5xl mx-auto relative z-10">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.3 }}
          variants={stagger}
          className="text-center mb-16"
        >
          <motion.span variants={fadeUp} custom={0} className="text-xs font-semibold uppercase tracking-widest text-accent">
            Real Data, Real APIs
          </motion.span>
          <motion.h2 variants={fadeUp} custom={1} className="text-3xl sm:text-4xl font-display font-bold mt-3">
            Powered by 4 Data Sources
          </motion.h2>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={stagger}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5"
        >
          {sources.map((s, i) => (
            <motion.div
              key={s.name}
              variants={fadeUp}
              custom={i}
              whileHover={{ y: -4 }}
               className="neo-box p-6 text-center"
             >
               <div className={`w-12 h-12 border-2 border-border grid place-items-center mx-auto mb-4 bg-surface ${s.color}`}>
                 <s.icon className="w-6 h-6" />
               </div>
              <h3 className="font-display font-bold mb-1">{s.name}</h3>
              <p className="text-xs text-sage mb-3">{s.desc}</p>
              <span className="inline-flex items-center gap-1.5 text-xs font-medium text-primary bg-primary/10 rounded-full px-3 py-1">
                <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                {s.status}
              </span>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   TRUST — Glass badges
   ═══════════════════════════════════════════════════════════════════ */
function TrustSection() {
  const badges = [
    { icon: BadgeCheck, label: "100% Public Data", desc: "ISRO, Sentinel-2, NASA SMAP, Open-Meteo — all open-access.", color: "text-primary" },
    { icon: WifiOff, label: "Offline-First", desc: "Works without internet. Soil DB bundled. Ideal for rural India.", color: "text-accent" },
    { icon: HeartHandshake, label: "Sustainability", desc: "Promotes crop rotation, soil health monitoring, and balance.", color: "text-gold" },
  ];

  return (
    <section id="trust" className="relative py-28 px-6">
      <div className="max-w-5xl mx-auto relative z-10">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.3 }}
          variants={stagger}
          className="text-center mb-14"
        >
          <motion.span variants={fadeUp} custom={0} className="text-xs font-semibold uppercase tracking-widest text-accent">
            Trust & Impact
          </motion.span>
          <motion.h2 variants={fadeUp} custom={1} className="text-3xl sm:text-4xl font-display font-bold mt-3">
            Built on Transparency
          </motion.h2>
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
              whileHover={{ y: -4 }}
               className="neo-box p-8 text-center"
             >
               <div className={`w-14 h-14 rounded-full border-2 border-border grid place-items-center mx-auto mb-5 bg-surface ${b.color}`}>
                 <b.icon className="w-6 h-6" />
               </div>
              <h3 className="font-display font-bold mb-2">{b.label}</h3>
              <p className="text-sm text-sage leading-relaxed">{b.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   CTA BAND — Glass CTA
   ═══════════════════════════════════════════════════════════════════ */
function CtaBand({ onLaunch }: { onLaunch: () => void }) {
  return (
    <section className="py-20 px-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.97 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true }}
         transition={{ duration: 0.5 }}
         className="max-w-4xl mx-auto neo-box relative overflow-hidden bg-primary"
       >
        {/* Glow behind */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-accent/10 pointer-events-none" />

        <div className="relative z-10 flex flex-col items-center text-center py-16 px-8">
          <h2 className="text-2xl sm:text-3xl font-display font-bold mb-3">
            Ready to farm smarter?
          </h2>
          <p className="text-sage mb-8 max-w-md">
            Enter the dashboard, type a question in plain language, and get satellite-backed answers in seconds.
          </p>
          <motion.button
             whileHover={{ scale: 1.05 }}
             whileTap={{ scale: 0.95 }}
             onClick={onLaunch}
             className="group inline-flex items-center gap-2 px-8 py-4 bg-text text-bg font-bold rounded-none shadow-neo hover:shadow-neo-lg transition-all"
           >
             <Rocket className="w-4 h-4" />
             Open Orbital Nexus
             <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
           </motion.button>
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
    <footer className="border-t-2 border-border bg-surface py-10 px-6">
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-sage">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg overflow-hidden">
            <img src="/logo.png" alt="Orbital Nexus" className="w-full h-full object-cover" />
          </div>
          <span className="font-display font-bold text-white/80">Orbital Nexus</span>
        </div>
        <p>Built with ❤️ in Ghaziabad · Hyperspace 2026</p>
        <div className="flex gap-5">
          <a href="#problem" className="hover:text-white transition">Problem</a>
          <a href="#solution" className="hover:text-white transition">Solution</a>
          <a href="#trust" className="hover:text-white transition">Trust</a>
        </div>
      </div>
    </footer>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   ORBIT DECORATION — SVG rings behind hero
   ═══════════════════════════════════════════════════════════════════ */
function OrbitDecoration() {
  return (
    <div className="pointer-events-none absolute inset-0 flex items-center justify-center opacity-[0.06]">
      <svg
        width="800"
        height="800"
        viewBox="0 0 800 800"
        fill="none"
        className="animate-[spin_100s_linear_infinite]"
      >
        <circle cx="400" cy="400" r="200" stroke="white" strokeWidth="0.5" />
        <circle cx="400" cy="400" r="290" stroke="white" strokeWidth="0.5" />
        <circle cx="400" cy="400" r="380" stroke="white" strokeWidth="0.5" />
        <circle cx="600" cy="400" r="5" fill="#10b981" />
        <circle cx="400" cy="110" r="4" fill="#06b6d4" />
        <circle cx="200" cy="560" r="4" fill="#60a5fa" />
        <circle cx="500" cy="150" r="3" fill="#f59e0b" />
      </svg>
    </div>
  );
}
