import {
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { useTranslation } from "react-i18next";

interface DataPoint {
  salario: number;
  capital_neto_total: number;
  capital_personal: number;
  capital_empresa: number;
}

interface Props {
  data: DataPoint[];
  autonomoLevel: number;
  optimalSalary: number;
  title: string;
}

const formatAxis = (v: number) => {
  if (Math.abs(v) >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M \u20ac`;
  return `${(v / 1000).toFixed(0)}K \u20ac`;
};

const formatCurrency = (v: number) =>
  v.toLocaleString("es-ES", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  });

const SalaryOptimizationChart = ({ data, autonomoLevel, optimalSalary, title }: Props) => {
  const { t } = useTranslation();

  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold">{title}</h3>
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 20, right: 20, left: 20, bottom: 5 }}>
            <defs>
              <linearGradient id="personalGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#60a5fa" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#60a5fa" stopOpacity={0.05} />
              </linearGradient>
              <linearGradient id="empresaGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#34d399" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#34d399" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="salario"
              tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}K \u20ac`}
              tick={{ fontSize: 12 }}
            />
            <YAxis tickFormatter={formatAxis} tick={{ fontSize: 12 }} />
            <Tooltip
              formatter={(value: number, name: string) => [formatCurrency(value), name]}
              labelFormatter={(label: number) =>
                `${t("charts.salary", "Salario")}: ${formatCurrency(label)}`
              }
              contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }}
            />
            <Legend verticalAlign="top" height={36} />
            <Area
              type="monotone"
              dataKey="capital_personal"
              stackId="1"
              stroke="#60a5fa"
              fill="url(#personalGrad)"
              name={t("charts.capital_personal", "Capital personal")}
            />
            <Area
              type="monotone"
              dataKey="capital_empresa"
              stackId="1"
              stroke="#34d399"
              fill="url(#empresaGrad)"
              name={t("charts.capital_empresa", "Capital empresa")}
            />
            <Line
              type="monotone"
              dataKey="capital_neto_total"
              stroke="#2563eb"
              strokeWidth={2}
              dot={false}
              name={t("charts.capital_neto_total", "Capital neto total")}
            />
            <ReferenceLine
              y={autonomoLevel}
              stroke="#dc2626"
              strokeDasharray="5 5"
              strokeWidth={2}
              label={{
                value: t("charts.autonomo", "Aut\u00f3nomo"),
                position: "right",
                fill: "#dc2626",
                fontSize: 12,
                fontWeight: 600,
              }}
            />
            {optimalSalary > 0 && (
              <ReferenceLine
                x={optimalSalary}
                stroke="#16a34a"
                strokeDasharray="5 5"
                strokeWidth={2}
                label={{
                  value: `${t("charts.optimal", "\u00d3ptimo")}: ${formatCurrency(optimalSalary)}`,
                  position: "top",
                  fill: "#16a34a",
                  fontSize: 12,
                  fontWeight: 600,
                }}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default SalaryOptimizationChart;
