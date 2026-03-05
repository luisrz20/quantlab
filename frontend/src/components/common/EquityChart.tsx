import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import type { EquityPoint } from "@/api/client";

interface Series {
  data: EquityPoint[];
  name: string;
  color: string;
}

interface Props {
  series: Series[];
  height?: number;
}

export default function EquityChart({ series, height = 300 }: Props) {
  // Merge all timestamps as x-axis keys
  const all = new Map<string, Record<string, number>>();
  series.forEach((s) => {
    s.data.forEach((pt) => {
      const label = pt.timestamp.slice(0, 10);
      const row = all.get(label) ?? {};
      row[s.name] = pt.equity;
      all.set(label, row);
    });
  });
  const chartData = Array.from(all.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, vals]) => ({ date, ...vals }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.07)" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 11 }}
          tickFormatter={(v: string) => v.slice(5)}
        />
        <YAxis
          tick={{ fontSize: 11 }}
          tickFormatter={(v: number) => `$${(v / 1000).toFixed(0)}k`}
          width={60}
        />
        <Tooltip
          formatter={(v: number) => [`$${v.toLocaleString()}`, ""]}
          contentStyle={{ background: "#1e293b", border: "1px solid #6366f1" }}
        />
        {series.length > 1 && <Legend />}
        {series.map((s) => (
          <Line
            key={s.name}
            type="monotone"
            dataKey={s.name}
            stroke={s.color}
            dot={false}
            strokeWidth={2}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
