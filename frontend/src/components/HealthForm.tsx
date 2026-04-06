import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronRight, ChevronLeft, Loader2, User, Cigarette, Stethoscope } from "lucide-react";
import type { HealthFormData, PredictionResult } from "../types";
import { predict } from "../api/cardionova";

const defaultForm: HealthFormData = {
  name: "",
  age: 45,
  male: 1,
  education: 2,
  currentSmoker: 0,
  cigsPerDay: 0,
  BPMeds: 0,
  prevalentStroke: 0,
  prevalentHyp: 0,
  diabetes: 0,
  totChol: 200,
  sysBP: 120,
  diaBP: 80,
  BMI: 25,
  heartRate: 75,
  glucose: 90,
};

interface Props {
  onResult: (result: PredictionResult, form: HealthFormData) => void;
}

const inputClass =
  "w-full bg-[#0d1829] border border-blue-900/50 rounded-xl px-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/30 transition-all text-sm";
const labelClass = "block text-slate-300 text-sm font-medium mb-1.5";
const selectClass = inputClass;
const stepIcons = [User, Cigarette, Stethoscope];
const stepLabels = ["Personal Details", "Lifestyle & History", "Clinical Measurements"];

export default function HealthForm({ onResult }: Props) {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState<HealthFormData>(defaultForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const set = (key: keyof HealthFormData, value: number) =>
    setForm((f) => ({ ...f, [key]: value }));

  const handleSubmit = async () => {
    setLoading(true);
    setError("");

    try {
      const result = await predict(form);
      console.log("RAW API RESPONSE:", JSON.stringify(result, null, 2));
      onResult(result, form);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(`Connection failed: ${message}. Make sure FastAPI is running on port 8000 with CORS enabled.`);
      console.error("Predict error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="min-h-screen bg-[#080f1a] flex items-center justify-center px-6 pt-28 pb-16">
      <div className="w-full max-w-lg">
        {/* Step tabs */}
        <div className="flex items-center justify-between mb-8 relative">
          <div className="absolute top-5 left-0 right-0 h-px bg-blue-900/40 z-0" />
          {stepLabels.map((label, i) => {
            const Icon = stepIcons[i];
            const active = i === step;
            const done = i < step;

            return (
              <div key={label} className="flex flex-col items-center gap-2 z-10 relative">
                <motion.div
                  animate={{
                    backgroundColor: active ? "#2563eb" : done ? "#1d4ed8" : "#0d1829",
                    borderColor: active || done ? "#3b82f6" : "#1e3a5f",
                    scale: active ? 1.15 : 1,
                  }}
                  transition={{ duration: 0.3 }}
                  className="w-10 h-10 rounded-full flex items-center justify-center border-2"
                >
                  <Icon className={`w-4 h-4 ${active || done ? "text-white" : "text-slate-600"}`} />
                </motion.div>
                <span
                  className={`text-[10px] font-medium text-center leading-tight hidden sm:block ${
                    active ? "text-blue-400" : done ? "text-slate-400" : "text-slate-600"
                  }`}
                  style={{ maxWidth: "70px" }}
                >
                  {label}
                </span>
              </div>
            );
          })}
        </div>

        {/* Card */}
        <div className="bg-[#0d1829] border border-blue-900/30 rounded-3xl p-8 shadow-2xl shadow-blue-900/20">
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -30 }}
              transition={{ duration: 0.3 }}
            >
              <h2 className="text-2xl font-bold text-white mb-1">{stepLabels[step]}</h2>
              <p className="text-slate-500 text-sm mb-6">Step {step + 1} of 3 - Fill in your details below</p>

              {/* Step 0 - Personal */}
              {step === 0 && (
                <div className="space-y-4">
                  <div>
                    <label className={labelClass}>Full Name</label>
                    <input
                      type="text"
                      className={inputClass}
                      placeholder="e.g. Robert Smith"
                      value={form.name}
                      onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className={labelClass}>Age (years)</label>
                    <input
                      type="number"
                      className={inputClass}
                      value={form.age}
                      onChange={(e) => set("age", +e.target.value)}
                    />
                  </div>
                  <div>
                    <label className={labelClass}>Biological Sex</label>
                    <select
                      className={selectClass}
                      value={form.male}
                      onChange={(e) => set("male", +e.target.value as 0 | 1)}
                    >
                      <option value={1}>Male</option>
                      <option value={0}>Female</option>
                    </select>
                  </div>
                  <div>
                    <label className={labelClass}>Highest Education Level</label>
                    <select
                      className={selectClass}
                      value={form.education}
                      onChange={(e) => set("education", +e.target.value as 1 | 2 | 3 | 4)}
                    >
                      <option value={1}>Some High School</option>
                      <option value={2}>High School / GED</option>
                      <option value={3}>Some College / Vocational</option>
                      <option value={4}>College Degree or Higher</option>
                    </select>
                  </div>
                </div>
              )}

              {/* Step 1 - Lifestyle */}
              {step === 1 && (
                <div className="space-y-4">
                  {([
                    ["Current Smoker?", "currentSmoker"],
                    ["On BP Medication?", "BPMeds"],
                    ["History of Stroke?", "prevalentStroke"],
                    ["Hypertension Diagnosed?", "prevalentHyp"],
                    ["Diabetes Diagnosed?", "diabetes"],
                  ] as [string, keyof HealthFormData][]).map(([label, key]) => (
                    <div key={key}>
                      <label className={labelClass}>{label}</label>
                      <select
                        className={selectClass}
                        value={form[key] as number}
                        onChange={(e) => set(key, +e.target.value as 0 | 1)}
                      >
                        <option value={0}>No</option>
                        <option value={1}>Yes</option>
                      </select>
                    </div>
                  ))}
                  {form.currentSmoker === 1 && (
                    <div>
                      <label className={labelClass}>Cigarettes per Day</label>
                      <input
                        type="number"
                        className={inputClass}
                        value={form.cigsPerDay}
                        onChange={(e) => set("cigsPerDay", +e.target.value)}
                      />
                    </div>
                  )}
                </div>
              )}

              {/* Step 2 - Clinical */}
              {step === 2 && (
                <div className="space-y-4">
                  {([
                    ["Total Cholesterol (mg/dL)", "totChol", "Normal: 125-200"],
                    ["Systolic BP (mmHg)", "sysBP", "Normal: < 120"],
                    ["Diastolic BP (mmHg)", "diaBP", "Normal: < 80"],
                    ["BMI (kg/m^2)", "BMI", "Normal: 18.5-24.9"],
                    ["Resting Heart Rate (bpm)", "heartRate", "Normal: 60-100"],
                    ["Glucose (mg/dL)", "glucose", "Normal: 70-100"],
                  ] as [string, keyof HealthFormData, string][]).map(([label, key, hint]) => (
                    <div key={key}>
                      <label className={labelClass}>
                        {label}
                        <span className="text-slate-600 font-normal ml-2 text-xs">{hint}</span>
                      </label>
                      <input
                        type="number"
                        className={inputClass}
                        value={form[key] as number}
                        onChange={(e) => set(key, +e.target.value)}
                      />
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          </AnimatePresence>

          {error && (
            <div className="mt-5 text-red-300 text-sm bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3">
              {error}
            </div>
          )}

          <div className="flex justify-between items-center mt-8">
            {step > 0 ? (
              <button
                onClick={() => setStep(step - 1)}
                className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors text-sm"
              >
                <ChevronLeft className="w-4 h-4" /> Back
              </button>
            ) : (
              <div />
            )}

            {step < 2 ? (
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => setStep(step + 1)}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold px-6 py-3 rounded-xl transition-colors text-sm"
              >
                Continue <ChevronRight className="w-4 h-4" />
              </motion.button>
            ) : (
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={handleSubmit}
                disabled={loading}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-60 text-white font-semibold px-6 py-3 rounded-xl transition-colors text-sm"
              >
                {loading && <Loader2 className="w-4 h-4 animate-spin" />}
                {loading ? "Analyzing..." : "Analyze My Risk ->"}
              </motion.button>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
