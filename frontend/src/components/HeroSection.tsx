import { motion } from "framer-motion";
import { ShieldCheck, Cpu, ChevronRight, Activity } from "lucide-react";

interface Props {
  onStart: () => void;
}

const stats = [
  { label: "Accuracy", value: "87%", icon: Cpu },
  { label: "Risk Factors", value: "15+", icon: Activity },
  { label: "Study Basis", value: "Framingham", icon: ShieldCheck },
];


export default function HeroSection({ onStart }: Props) {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-[#080f1a]">
      {/* Background grid */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage:
            "linear-gradient(#3b82f6 1px, transparent 1px), linear-gradient(90deg, #3b82f6 1px, transparent 1px)",
          backgroundSize: "50px 50px",
        }}
      />

      {/* Glow orbs */}
      <motion.div
        animate={{ scale: [1, 1.15, 1], opacity: [0.12, 0.2, 0.12] }}
        transition={{ duration: 9, repeat: Infinity }}
        className="absolute top-1/4 left-1/3 w-[500px] h-[500px] bg-blue-600 rounded-full blur-[120px] pointer-events-none"
      />
      <motion.div
        animate={{ scale: [1.1, 1, 1.1], opacity: [0.08, 0.15, 0.08] }}
        transition={{ duration: 11, repeat: Infinity }}
        className="absolute bottom-1/4 right-1/3 w-[400px] h-[400px] bg-cyan-500 rounded-full blur-[100px] pointer-events-none"
      />

      <div className="relative z-10 text-center px-6 max-w-4xl mx-auto">
        

        {/* Heading */}
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-5xl md:text-7xl font-extrabold text-white mb-6 leading-[1.1] tracking-tight"
        >
          Predict Your
          <br />
          <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-300 bg-clip-text text-transparent">
            Cardiovascular Risk
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-slate-400 text-lg md:text-xl mb-12 max-w-2xl mx-auto leading-relaxed"
        >
          Clinical-grade AI analysis of your 10-year cardiovascular disease risk.
          Get a detailed PDF report with SHAP-explained insights — free, instant,
          no account needed.
        </motion.p>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16"
        >
          <motion.button
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.97 }}
            onClick={onStart}
            className="group flex items-center gap-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold text-base px-8 py-4 rounded-2xl transition-all shadow-xl shadow-blue-600/30"
          >
            Start Free Assessment
            <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </motion.button>
          <span className="text-slate-500 text-sm">
            ~2 min · No signup · Instant PDF
          </span>
        </motion.div>

        {/* Stats row */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.4 }}
          className="grid grid-cols-3 gap-4 max-w-xl mx-auto"
        >
          {stats.map(({ label, value, icon: Icon }) => (
            <div
              key={label}
              className="bg-white/[0.03] border border-white/[0.07] rounded-2xl p-4 flex flex-col items-center gap-1"
            >
              <Icon className="w-4 h-4 text-blue-400 mb-1" />
              <span className="text-white font-bold text-xl">{value}</span>
              <span className="text-slate-500 text-xs">{label}</span>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
