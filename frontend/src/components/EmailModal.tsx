import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Mail, Loader2, CheckCircle2, Send } from "lucide-react";
import type { HealthFormData } from "../types";
import { sendReport } from "../api/cardionova";

interface Props {
  formData: HealthFormData;
  predictionId: string;        // ← add this
  onClose: () => void;
}

export default function EmailModal({ formData, predictionId, onClose }: Props) {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  const handleSend = async () => {
    if (!email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      setError("Please enter a valid email address.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      await sendReport(formData, email, predictionId);  // ← pass predictionId
      setSent(true);
    } catch (err) {
      console.error("Send report error:", err);
      setError("Failed to send. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center px-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.92, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.92, opacity: 0 }}
          transition={{ type: "spring", stiffness: 280, damping: 24 }}
          className="bg-[#0d1829] border border-blue-900/40 rounded-3xl p-8 w-full max-w-md relative shadow-2xl shadow-blue-900/30"
          onClick={(e) => e.stopPropagation()}
        >
          <button onClick={onClose}
            className="absolute top-5 right-5 text-slate-500 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>

          {!sent ? (
            <>
              <div className="w-12 h-12 bg-blue-500/10 border border-blue-500/20 rounded-2xl flex items-center justify-center mb-5">
                <Mail className="w-5 h-5 text-blue-400" />
              </div>
              <h3 className="text-white text-xl font-bold mb-1">Email Your Report</h3>
              <p className="text-slate-500 text-sm mb-6">
                Your full 4-page clinical PDF will be delivered to your inbox instantly.
              </p>
              <input
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                className="w-full bg-[#080f1a] border border-blue-900/50 rounded-xl px-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/30 transition-all text-sm mb-3"
              />
              {error && (
                <p className="text-red-400 text-xs mb-3 bg-red-500/10 border border-red-500/20 px-3 py-2 rounded-lg">
                  {error}
                </p>
              )}
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.97 }}
                onClick={handleSend}
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-60 text-white font-semibold py-3 rounded-xl transition-colors text-sm"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                {loading ? "Sending Report..." : "Send Report"}
              </motion.button>
            </>
          ) : (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-4"
            >
              <CheckCircle2 className="w-16 h-16 text-emerald-400 mx-auto mb-4" />
              <h3 className="text-white text-xl font-bold mb-2">Report Sent!</h3>
              <p className="text-slate-400 text-sm mb-1">Successfully delivered to</p>
              <p className="text-blue-300 font-medium text-sm">{email}</p>
              <button onClick={onClose}
                className="mt-6 bg-[#080f1a] hover:bg-blue-900/30 border border-blue-900/40 text-white px-8 py-3 rounded-xl transition-colors text-sm">
                Close
              </button>
            </motion.div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

