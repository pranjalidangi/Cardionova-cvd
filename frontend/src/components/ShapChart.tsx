import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import type { ShapFactor } from "../types";

interface Props {
  factors: ShapFactor[];
}

const COLORS = ["#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe", "#dbeafe"];

export default function ShapChart({ factors }: Props) {
  const data = factors.map((f) => ({
    name: f.feature.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
    value: parseFloat(Math.abs(f.value).toFixed(4)),
  }));

  return (
    <ResponsiveContainer width="100%" height={230}>
      <BarChart data={data} layout="vertical" margin={{ left: 8, right: 24, top: 4, bottom: 4 }}>
        <XAxis
          type="number"
          tick={{ fill: "#475569", fontSize: 11 }}
          axisLine={{ stroke: "#1e3a5f" }}
          tickLine={false}
        />
        <YAxis
          type="category"
          dataKey="name"
          tick={{ fill: "#94a3b8", fontSize: 12 }}
          width={120}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          contentStyle={{ backgroundColor: "#0d1829", border: "1px solid #1e3a5f", borderRadius: 12, fontSize: 12 }}
          labelStyle={{ color: "#e2e8f0" }}
          itemStyle={{ color: "#60a5fa" }}
          formatter={(value) => [(value as number).toFixed(4), "SHAP Impact"]}
        />
        <Bar dataKey="value" radius={[0, 8, 8, 0]}>
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i] || "#3b82f6"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
