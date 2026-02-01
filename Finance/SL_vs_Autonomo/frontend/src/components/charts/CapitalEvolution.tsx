import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
  CartesianGrid,
} from "recharts";
import { useTranslation } from "react-i18next";

interface CapitalDataPoint {
  ano: number;
  employee?: number;
  autonomo?: number;
  sl?: number;
}

interface CapitalEvolutionProps {
  data: CapitalDataPoint[];
  title: string;
}

const COLORS: Record<string, string> = {
  employee: "#2563eb",
  autonomo: "#059669",
  sl: "#9333ea",
};

const formatCurrency = (v: number) =>
  v.toLocaleString("es-ES", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });

const CapitalEvolution = ({ data, title }: CapitalEvolutionProps) => {
  const { t } = useTranslation();

  const lineKeys = Object.keys(data[0] || {}).filter((k) => k !== "ano");

  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold">{title}</h3>
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 20, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="ano"
              tick={{ fontSize: 12 }}
              label={{ value: t("charts.years", "Años"), position: "insideBottomRight", offset: -5 }}
            />
            <YAxis
              tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k €`}
              tick={{ fontSize: 12 }}
            />
            <Tooltip
              formatter={(value: number) => [formatCurrency(value)]}
              labelFormatter={(label: number) => `${t("charts.year", "Año")} ${label}`}
              contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }}
            />
            <Legend verticalAlign="top" height={36} />
            {lineKeys.map((key) => (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                stroke={COLORS[key] || "#6b7280"}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 5, strokeWidth: 2 }}
                name={t(`charts.${key}`, key)}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default CapitalEvolution;
