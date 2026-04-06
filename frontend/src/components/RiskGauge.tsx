import { PieChart, Pie, Cell } from "recharts";
import type { RiskLevel } from "../types";


interface Props {
  probability: number;
  riskLevel: RiskLevel;
}

const riskConfig: Record<RiskLevel, { color: string; bg: string; label: string; desc: string }> = {
  LOW:      { color: "#10b981", bg: "#10b98115", label: "Low Risk",      desc: "Your risk is within a healthy range." },
  MODERATE: { color: "#f59e0b", bg: "#f59e0b15", label: "Moderate Risk", desc: "Some risk factors need attention." },
  HIGH:     { color: "#ef4444", bg: "#ef444415", label: "High Risk",     desc: "Consult a cardiologist promptly." },
};

export default function RiskGauge({ probability, riskLevel }: Props) {
  const pct = Math.round(probability * 100);
  const { color, bg, label, desc } = riskConfig[riskLevel];
  const data = [{ value: pct }, { value: 100 - pct }];

  return (
    <div className="flex flex-col items-center">
      <div className="relative">
        <PieChart width={180} height={100}>
          <Pie
            data={data}
            cx={90} cy={95}
            startAngle={180} endAngle={0}
            innerRadius={55} outerRadius={82}
            dataKey="value"
            stroke="none"
          >
            <Cell fill={color} />
            <Cell fill="#0d1829" />
          </Pie>
        </PieChart>
        <div className="absolute inset-0 flex flex-col items-center justify-end pb-1">
          <span className="text-3xl font-extrabold text-white">{pct}%</span>
        </div>
      </div>
      <div
        className="mt-3 px-4 py-1.5 rounded-full text-sm font-semibold border"
        style={{ color, backgroundColor: bg, borderColor: `${color}40` }}
      >
        {label}
      </div>
      <p className="text-slate-500 text-xs mt-2 text-center max-w-[180px]">{desc}</p>
    </div>
  );
}
