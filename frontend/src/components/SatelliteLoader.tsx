import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

/**
 * SatelliteLoader — Sci-fi loading animation
 *
 * Shows a radar scan + orbiting dots with cycling status messages
 * that simulate satellite handshake sequence.
 */

const STATUS_MESSAGES = [
  "Acquiring GPS lock...",
  "Handshaking with Sentinel-2...",
  "Fetching NDVI thermal layers...",
  "Processing market vectors...",
  "Correlating soil moisture data...",
  "Fusing satellite sources...",
];

export default function SatelliteLoader() {
  const [msgIndex, setMsgIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setMsgIndex((prev) => (prev + 1) % STATUS_MESSAGES.length);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fixed inset-0 z-[9999] bg-nexus-dark/95 backdrop-blur-sm flex flex-col items-center justify-center gap-8">
      {/* Radar container */}
      <div className="relative w-40 h-40">
        {/* Outer ring */}
        <div className="absolute inset-0 rounded-full border border-emerald-500/20" />
        {/* Middle ring */}
        <div className="absolute inset-4 rounded-full border border-emerald-500/15" />
        {/* Inner ring */}
        <div className="absolute inset-8 rounded-full border border-emerald-500/10" />

        {/* Radar sweep — rotating gradient cone */}
        <motion.div
          className="absolute inset-0"
          animate={{ rotate: 360 }}
          transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
        >
          <div
            className="w-full h-full rounded-full"
            style={{
              background:
                "conic-gradient(from 0deg, transparent 0deg, rgba(52,211,153,0.25) 30deg, transparent 60deg)",
            }}
          />
        </motion.div>

        {/* Center dot */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-3 h-3 rounded-full bg-emerald-400 shadow-lg shadow-emerald-400/50" />
        </div>

        {/* Orbiting satellite 1 */}
        <motion.div
          className="absolute inset-0"
          animate={{ rotate: 360 }}
          transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
        >
          <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2">
            <div className="w-2 h-2 rounded-full bg-cyan-400 shadow-md shadow-cyan-400/50" />
          </div>
        </motion.div>

        {/* Orbiting satellite 2 — opposite direction */}
        <motion.div
          className="absolute inset-0"
          animate={{ rotate: -360 }}
          transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
        >
          <div className="absolute bottom-2 right-0 translate-x-1/2">
            <div className="w-1.5 h-1.5 rounded-full bg-blue-400 shadow-md shadow-blue-400/50" />
          </div>
        </motion.div>

        {/* Ping ripple */}
        <motion.div
          className="absolute inset-0 rounded-full border border-emerald-400/30"
          animate={{ scale: [1, 1.8], opacity: [0.4, 0] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeOut" }}
        />
      </div>

      {/* Status message — animated swap */}
      <div className="h-6 flex items-center">
        <AnimatePresence mode="wait">
          <motion.p
            key={msgIndex}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.3 }}
            className="text-sm font-mono text-emerald-400/80 tracking-wide"
          >
            {STATUS_MESSAGES[msgIndex]}
          </motion.p>
        </AnimatePresence>
      </div>

      {/* Subtle progress dots */}
      <div className="flex gap-1.5">
        {STATUS_MESSAGES.map((_, i) => (
          <div
            key={i}
            className={`w-1.5 h-1.5 rounded-full transition-colors duration-300 ${
              i <= msgIndex ? "bg-emerald-400" : "bg-gray-700"
            }`}
          />
        ))}
      </div>
    </div>
  );
}
