import { Heart } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-[#080f1a] border-t border-blue-900/20 py-10 px-6">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Heart className="w-4 h-4 text-blue-400" fill="currentColor" />
          <span className="text-white font-semibold text-sm">
            Cardio<span className="text-blue-400">nova</span>
          </span>
          <span className="text-slate-700 text-sm mx-2">·</span>
          <span className="text-slate-600 text-xs">AI Cardiovascular Risk Prediction</span>
        </div>
        <p className="text-slate-700 text-xs text-center">
          For educational purposes only — not a substitute for medical advice
        </p>
        <p className="text-slate-700 text-xs">
          Pranjali Dangi · EN23CS301768 · Medicaps University · 2026
        </p>
      </div>
    </footer>
  );
}
