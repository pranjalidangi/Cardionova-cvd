import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import Navbar from "./components/Navbar";
import HeroSection from "./components/HeroSection";
import HealthForm from "./components/HealthForm";
import Dashboard from "./components/Dashboard";
import EmailModal from "./components/EmailModal";
import Footer from "./components/Footer";
import type { PredictionResult, HealthFormData } from "./types";

type View = "hero" | "form" | "dashboard";

export default function App() {
  const [view, setView] = useState<View>("hero");
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [formData, setFormData] = useState<HealthFormData | null>(null);
  const [showEmail, setShowEmail] = useState(false);

  const handleResult = (r: PredictionResult, f: HealthFormData) => {
    setResult(r);
    setFormData(f);
    setView("dashboard");
  };

  return (
    <div className="min-h-screen bg-[#080f1a]">
      <Navbar />
      <AnimatePresence mode="wait">
        {view === "hero" && (
          <motion.div
            key="hero"
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
            transition={{ duration: 0.45, ease: "easeOut" }}
          >
            <HeroSection onStart={() => setView("form")} />
          </motion.div>
        )}
        {view === "form" && (
          <motion.div
            key="form"
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
            transition={{ duration: 0.45, ease: "easeOut" }}
          >
            <HealthForm onResult={handleResult} />
          </motion.div>
        )}
        {view === "dashboard" && result && formData && (
          <motion.div
            key="dashboard"
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
            transition={{ duration: 0.45, ease: "easeOut" }}
          >
            <Dashboard
              result={result}
              formData={formData}
              onEmailClick={() => setShowEmail(true)}
              onRetake={() => { setResult(null); setFormData(null); setView("hero"); }}
            />
          </motion.div>
        )}
      </AnimatePresence>
      {showEmail && formData && result && (
        <EmailModal
          formData={formData}
          predictionId={result.prediction_id}   // ← add this
          onClose={() => setShowEmail(false)}
        />
      )}
      <Footer />
    </div>
  );
}
