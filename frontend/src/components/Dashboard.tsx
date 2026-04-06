import { motion } from "framer-motion";
import {
  Download, Mail, Activity, Droplets, Heart, TrendingUp,
  RotateCcw, AlertTriangle, CheckCircle, Info,
} from "lucide-react";
import type { PredictionResult, HealthFormData, RiskLevel } from "../types";


import RiskGauge from "./RiskGauge";
import ShapChart from "./ShapChart";
import { downloadReport } from "../api/cardionova";

interface Props {
  result: PredictionResult;
  formData: HealthFormData;
  onEmailClick: () => void;
  onRetake: () => void;
}

// Replace the entire riskBanner constant with this:
const riskBanner: Record<RiskLevel, { icon: typeof AlertTriangle; color: string; bg: string; border: string }> = {
  LOW: {
    icon: CheckCircle,
    color: "text-emerald-400",
    bg: "bg-emerald-500/5",
    border: "border-emerald-500/20",
  },
  MODERATE: {
    icon: Info,
    color: "text-amber-400",
    bg: "bg-amber-500/5",
    border: "border-amber-500/20",
  },
  HIGH: {
    icon: AlertTriangle,
    color: "text-red-400",
    bg: "bg-red-500/5",
    border: "border-red-500/20",
  },
};


export default function Dashboard({ result, formData, onEmailClick, onRetake }: Props) {
  const { risk_probability, risk_level, top_shap_factors } = result;
  const banner = riskBanner[risk_level];
  const BannerIcon = banner.icon;

  const handleDownload = async () => {
    const blob = await downloadReport(formData);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "cardionova-report.pdf";
    a.click();
    URL.revokeObjectURL(url);
  };

  const stats = [
    { label: "Systolic BP", value: `${formData.sysBP} mmHg`, icon: Activity, normal: formData.sysBP < 120 },
    { label: "Glucose",     value: `${formData.glucose} mg/dL`, icon: Droplets, normal: formData.glucose < 100 },
    { label: "Heart Rate",  value: `${formData.heartRate} bpm`, icon: Heart, normal: formData.heartRate >= 60 && formData.heartRate <= 100 },
    { label: "BMI",         value: formData.BMI.toString(), icon: TrendingUp, normal: formData.BMI >= 18.5 && formData.BMI <= 24.9 },
  ];

  return (
    <section className="min-h-screen bg-[#080f1a] pt-28 pb-20 px-6">
      <div className="max-w-5xl mx-auto">

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
          <h2 className="text-3xl font-extrabold text-white">
            {formData.name ? `${formData.name}'s Risk Assessment` : "Your Risk Assessment"}
          </h2>
          <p className="text-slate-500 text-sm mt-1">
            AI analysis based on Framingham Heart Study · Generated just now
          </p>
        </motion.div>


        {/* Banner */}
        {/* Banner */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className={`flex items-start gap-3 ${banner.bg} border ${banner.border} rounded-2xl px-5 py-4 mb-6`}
          >
          <BannerIcon className={`w-5 h-5 mt-0.5 shrink-0 ${banner.color}`} />
          <p className={`text-sm ${banner.color} font-medium`}>
            {result.recommendation}
          </p>
        </motion.div>


        {/* Top row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-5">
          {/* Gauge */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.15 }}
            className="bg-[#0d1829] border border-blue-900/30 rounded-3xl p-6 flex flex-col items-center justify-center"
          >
            <p className="text-slate-400 text-xs font-semibold uppercase tracking-widest mb-4">
              10-Year CVD Risk
            </p>
            <RiskGauge probability={risk_probability} riskLevel={risk_level} />
          </motion.div>

          {/* Stats */}
          <div className="lg:col-span-2 grid grid-cols-2 gap-4">
            {stats.map(({ label, value, icon: Icon, normal }, i) => (
              <motion.div
                key={label}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + i * 0.07 }}
                className="bg-[#0d1829] border border-blue-900/30 rounded-2xl p-5 flex items-center gap-4"
              >
                <div className={`p-3 rounded-xl ${normal ? "bg-emerald-500/10" : "bg-amber-500/10"}`}>
                  <Icon className={`w-5 h-5 ${normal ? "text-emerald-400" : "text-amber-400"}`} />
                </div>
                <div>
                  <p className="text-slate-500 text-xs">{label}</p>
                  <p className="text-white font-bold text-lg leading-tight">{value}</p>
                  <span className={`text-[10px] font-medium ${normal ? "text-emerald-500" : "text-amber-500"}`}>
                    {normal ? "Normal" : "Elevated"}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* SHAP Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="bg-[#0d1829] border border-blue-900/30 rounded-3xl p-6 mb-5"
        >
          <div className="mb-5">
            <h3 className="text-white font-bold text-lg">AI Risk Driver Analysis</h3>
            <p className="text-slate-500 text-sm mt-1">
              SHAP values show which factors contribute most to your predicted risk score.
            </p>
          </div>
          <ShapChart factors={top_shap_factors ?? []} />
        </motion.div>

        {/* Top 3 factor cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {(top_shap_factors ?? []).slice(0, 3).map((f, i) => (
            <motion.div
              key={f.feature}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.42 + i * 0.08 }}
              className="bg-[#0d1829] border border-blue-900/30 rounded-2xl p-5"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="w-7 h-7 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-bold flex items-center justify-center">
                  #{i + 1}
                </span>
                <span className="text-[10px] text-slate-600 uppercase tracking-wider">Top Factor</span>
              </div>
              <p className="text-white font-semibold text-sm capitalize mb-1">
                {f.feature.replace(/_/g, " ")}
              </p>
              <p className="text-blue-300 font-bold text-xl">{Math.abs(f.value).toFixed(4)}</p>
              <p className="text-slate-600 text-xs mt-1">SHAP impact score</p>
            </motion.div>
          ))}
        </div>

        {/* Buttons */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="flex flex-wrap items-center gap-4"
        >
          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            onClick={handleDownload}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold px-6 py-3 rounded-xl transition-all shadow-lg shadow-blue-600/25 text-sm"
          >
            <Download className="w-4 h-4" /> Download PDF Report
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            onClick={onEmailClick}
            className="flex items-center gap-2 bg-[#0d1829] hover:bg-blue-900/30 border border-blue-900/40 text-white font-semibold px-6 py-3 rounded-xl transition-colors text-sm"
          >
            <Mail className="w-4 h-4" /> Email Report
          </motion.button>
          <button
            onClick={onRetake}
            className="flex items-center gap-2 text-slate-500 hover:text-slate-300 text-sm transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" /> Retake Assessment
          </button>
        </motion.div>

        {/* Disclaimer */}
        <p className="text-slate-700 text-xs mt-8 leading-relaxed max-w-2xl">
          ⚕️ This tool is for educational and informational purposes only. It is not a substitute
          for professional medical advice, diagnosis, or treatment. Always consult a qualified
          healthcare provider.
        </p>
      </div>
    </section>
  );
}
