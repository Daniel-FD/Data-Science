import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
  CartesianGrid,
  ReferenceLine,
} from "recharts";
import { useTranslation } from "react-i18next";

interface CrossoverPoint {
  income: number;
  employee_net: number;
  autonomo_net: number;
  sl_net: number;
}

interface CrossoverChartProps {
  points: CrossoverPoint[];
  crossovers: number[];
  title?: string;
}

const formatCurrency = (v: number) =>
  v.toLocaleString("es-ES", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });

const CrossoverChart = ({ points, crossovers, title }: CrossoverChartProps) => {
  const { t } = useTranslation();

  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">
      {title && <h3 className="mb-4 text-lg font-semibold">{title}</h3>}
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={points} margin={{ top: 10, right: 20, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="income"
              tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k`}
              tick={{ fontSize: 12 }}
              label={{
                value: t("charts.annualIncome", "Facturación anual"),
                position: "insideBottomRight",
                offset: -5,
              }}
            />
            <YAxis
              tickFormatter={(v: number) => `${(v / 1000).toFixed(1)}k`}
              tick={{ fontSize: 12 }}
              label={{
                value: t("charts.monthlyNet", "Neto mensual (€)"),
                angle: -90,
                position: "insideLeft",
                offset: 10,
              }}
            />
            <Tooltip
              formatter={(value: number, name: string) => [formatCurrency(value), name]}
              labelFormatter={(label: number) =>
                `${t("charts.income", "Facturación")}: ${formatCurrency(label)}`
              }
              contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }}
            />
            <Legend verticalAlign="top" height={36} />
            <Line
              type="monotone"
              dataKey="autonomo_net"
              stroke="#059669"
              strokeWidth={2}
              dot={false}
              name={t("charts.autonomo", "Autónomo")}
            />
            <Line
              type="monotone"
              dataKey="sl_net"
              stroke="#9333ea"
              strokeWidth={2}
              dot={false}
              name={t("charts.sl", "SL")}
            />
            {crossovers.map((x, i) => (
              <ReferenceLine
                key={i}
                x={x}
                stroke="#ea580c"
                strokeDasharray="5 5"
                strokeWidth={2}
                label={{
                  value: `${formatCurrency(x)}`,
                  position: "top",
                  fill: "#ea580c",
                  fontSize: 11,
                  fontWeight: 600,
                }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default CrossoverChart;
