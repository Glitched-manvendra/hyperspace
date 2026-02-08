import { motion } from "framer-motion";
import { Thermometer, CloudRain, Droplets, Leaf, Activity } from "lucide-react";

interface AnimatedIconProps {
    type: string;
    className?: string;
    color?: string;
}

/**
 * AnimatedIcon - Renders professional animated icons based on the metric type.
 * Uses Framer Motion for subtle, non-distracting animations.
 */
export default function AnimatedIcon({ type, className = "", color: _color = "currentColor" }: AnimatedIconProps) {
    const normalizedType = type.toLowerCase();

    // Common icon props
    const iconProps = {
        className: `w-8 h-8 ${className}`,
        strokeWidth: 1.5,
    };

    switch (normalizedType) {
        case "temperature":
            return (
                <div className="relative">
                    <motion.div
                        animate={{ y: [0, -2, 0] }}
                        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                    >
                        <Thermometer {...iconProps} className={`${className} text-orange-500`} />
                    </motion.div>
                    {/* Subtle heat waves */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.5, y: 10 }}
                        animate={{ opacity: [0, 0.5, 0], scale: 1.2, y: -5 }}
                        transition={{ duration: 1.5, repeat: Infinity, ease: "easeOut", delay: 0.5 }}
                        className="absolute top-0 right-0 w-2 h-2 rounded-full bg-orange-400 blur-sm"
                    />
                </div>
            );

        case "rainfall":
            return (
                <div className="relative">
                    <motion.div
                        animate={{ y: [0, -1, 0] }}
                        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                    >
                        <CloudRain {...iconProps} className={`${className} text-blue-500`} />
                    </motion.div>
                    {/* Falling drops */}
                    <motion.div
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: [0, 1, 0], y: 15 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="absolute bottom-1 left-2 w-0.5 h-1.5 bg-blue-400 rounded-full"
                    />
                    <motion.div
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: [0, 1, 0], y: 15 }}
                        transition={{ duration: 1.2, repeat: Infinity, ease: "linear", delay: 0.3 }}
                        className="absolute bottom-1 right-3 w-0.5 h-1.5 bg-blue-400 rounded-full"
                    />
                </div>
            );

        case "soil moisture":
        case "moisture":
            return (
                <div className="relative">
                    <Droplets {...iconProps} className={`${className} text-cyan-600`} />
                    <motion.div
                        className="absolute inset-0 bg-cyan-400/20 rounded-full blur-md"
                        animate={{ scale: [0.8, 1.1, 0.8], opacity: [0.2, 0.4, 0.2] }}
                        transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
                    />
                </div>
            );

        case "ndvi":
        case "vegetation":
            return (
                <div className="relative">
                    <motion.div
                        animate={{ rotate: [0, 5, 0, -5, 0] }}
                        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                        style={{ originY: 1 }}
                    >
                        <Leaf {...iconProps} className={`${className} text-green-600`} />
                    </motion.div>
                    {/* Floating subtle particle */}
                    <motion.div
                        animate={{ y: [0, -5, 0], x: [0, 3, 0], opacity: [0, 0.6, 0] }}
                        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 1 }}
                        className="absolute top-0 right-0 w-1 h-1 bg-green-400 rounded-full"
                    />
                </div>
            );

        default:
            return (
                <motion.div
                    animate={{ scale: [1, 1.05, 1] }}
                    transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                >
                    <Activity {...iconProps} className={`${className} text-gray-500`} />
                </motion.div>
            );
    }
}
