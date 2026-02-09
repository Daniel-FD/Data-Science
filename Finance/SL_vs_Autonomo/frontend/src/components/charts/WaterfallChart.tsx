import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LabelList,
} from "recharts";
import { useTranslation } from "react-i18next";

interface WaterfallItem {
  label: string;
  amount: number;
  color: string;
}

interface WaterfallChartProps {
  items: WaterfallItem[];
  title: string;
}

const formatCurrency = (v: number) =>
  v.toLocaleString("es-ES", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });

const WaterfallChart = ({ items, title }: WaterfallChartProps) => {
  const { t } = useTranslation();

  // Build waterfall data: each bar has an invisible base and a visible segment.
  let running = 0;
  const chartData = items.map((item) => {
    const isPositive = item.amount >= 0;
    const base = isPositive ? running : running + item.amount;
    const visible = Math.abs(item.amount);
    running += item.amount;
    return {
      label: item.label,
      base,
      visible,
      amount: item.amount,
      color: item.color,
      total: running,
    };
  });

  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold">{title}</h3>
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 20, right: 20, left: 20, bottom: 5 }}>
            <XAxis
              dataKey="label"
              tick={{ fontSize: 12 }}
              interval={0}
              angle={-30}
              textAnchor="end"
              height={60}
            />
            <YAxis
              tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k`}
              tick={{ fontSize: 12 }}
            />
            <Tooltip
              formatter={(value: number, name: string) => {
                if (name === "base") return [null, null];
                return [formatCurrency(value), t("charts.amount", "Cantidad")];
              }}
              labelFormatter={(label: string) => label}
              contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }}
            />
            {/* Invisible base bar */}
            <Bar dataKey="base" stackId="waterfall" fill="transparent" isAnimationActive={false} />
            {/* Visible segment */}
            <Bar dataKey="visible" stackId="waterfall" radius={[4, 4, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={index} fill={entry.color} />
              ))}
              <LabelList
                dataKey="amount"
                position="top"
                formatter={(v: number) => formatCurrency(v)}
                style={{ fontSize: 11, fontWeight: 500 }}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default WaterfallChart;
