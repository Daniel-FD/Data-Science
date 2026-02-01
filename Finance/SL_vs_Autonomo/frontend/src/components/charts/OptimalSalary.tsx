import {
  AreaChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceLine,
  Legend,
} from "recharts";
import { useTranslation } from "react-i18next";

interface OptimalSalaryDataPoint {
  salary: number;
  net_income: number;
  total_impuestos: number;
}

interface OptimalSalaryProps {
  curve: OptimalSalaryDataPoint[];
  optimalSalary: number;
  title?: string;
}

const formatCurrency = (v: number) =>
  v.toLocaleString("es-ES", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });

const OptimalSalary = ({ curve, optimalSalary, title }: OptimalSalaryProps) => {
  const { t } = useTranslation();

  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">
      {title && <h3 className="mb-4 text-lg font-semibold">{title}</h3>}
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={curve} margin={{ top: 20, right: 20, left: 20, bottom: 5 }}>
            <defs>
              <linearGradient id="netIncomeGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#059669" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#059669" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="salary"
              tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k`}
              tick={{ fontSize: 12 }}
              label={{
                value: t("charts.salary", "Salario bruto (€)"),
                position: "insideBottomRight",
                offset: -5,
              }}
            />
            <YAxis
              tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k`}
              tick={{ fontSize: 12 }}
            />
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
              dataKey="net_income"
              stroke="#059669"
              strokeWidth={2}
              fill="url(#netIncomeGradient)"
              name={t("charts.netIncome", "Renta neta")}
            />
            <Line
              type="monotone"
              dataKey="total_impuestos"
              stroke="#dc2626"
              strokeWidth={2}
              strokeDasharray="6 4"
              dot={false}
              name={t("charts.totalTaxes", "Impuestos totales")}
            />
            <ReferenceLine
              x={optimalSalary}
              stroke="#ea580c"
              strokeDasharray="5 5"
              strokeWidth={2}
              label={{
                value: `${t("charts.optimal", "Óptimo")}: ${formatCurrency(optimalSalary)}`,
                position: "top",
                fill: "#ea580c",
                fontSize: 12,
                fontWeight: 600,
              }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default OptimalSalary;
