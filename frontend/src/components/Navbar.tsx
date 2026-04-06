import { motion } from "framer-motion";
import { Heart } from "lucide-react";

export default function Navbar() {
  return (
    <motion.nav
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="fixed top-0 w-full z-50 bg-[#080f1a]/90 backdrop-blur-xl border-b border-blue-900/30"
    >
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-600/20 rounded-xl border border-blue-500/30">
            <Heart className="w-5 h-5 text-blue-400" fill="currentColor" />
          </div>
          <div>
            <span className="text-white font-bold text-lg tracking-tight">
              Cardio<span className="text-blue-400">nova</span>
            </span>
            <p className="text-slate-500 text-[10px] leading-none mt-0.5 tracking-widest uppercase">
              AI Heart Risk Analysis
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-emerald-400 text-xs font-medium">System Online</span>
        </div>
      </div>
    </motion.nav>
  );
}
