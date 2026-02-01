import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";

interface PieItem {
  label: string;
  amount: number;
  color: string;
}

interface IncomeBreakdownPieProps {
  items: PieItem[];
  title: string;
}

const formatCurrency = (v: number) =>
  v.toLocaleString("es-ES", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });

const RADIAN = Math.PI / 180;

const renderLabel = ({
  cx,
  cy,
  midAngle,
  innerRadius,
  outerRadius,
  percent,
}: {
  cx: number;
  cy: number;
  midAngle: number;
  innerRadius: number;
  outerRadius: number;
  percent: number;
}) => {
  const radius = innerRadius + (outerRadius - innerRadius) * 1.4;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  if (percent < 0.05) return null;

  return (
    <text x={x} y={y} fill="#475569" textAnchor={x > cx ? "start" : "end"} fontSize={12}>
      {(percent * 100).toFixed(1)}%
    </text>
  );
};

const CenterLabel = ({ viewBox, total }: { viewBox?: { cx: number; cy: number }; total: number }) => {
  if (!viewBox) return null;
  const { cx, cy } = viewBox;
  return (
    <>
      <text x={cx} y={cy - 8} textAnchor="middle" fill="#1e293b" fontSize={16} fontWeight={600}>
        {formatCurrency(total)}
      </text>
      <text x={cx} y={cy + 14} textAnchor="middle" fill="#94a3b8" fontSize={12}>
        Total
      </text>
    </>
  );
};

const IncomeBreakdownPie = ({ items, title }: IncomeBreakdownPieProps) => {
  const total = items.reduce((sum, i) => sum + i.amount, 0);
  const data = items.map((i) => ({ name: i.label, value: i.amount, color: i.color }));

  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold">{title}</h3>
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="45%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={2}
              label={renderLabel}
              labelLine={false}
            >
              {data.map((entry, index) => (
                <Cell key={index} fill={entry.color} stroke="white" strokeWidth={2} />
              ))}
              <CenterLabel total={total} />
            </Pie>
            <Tooltip
              formatter={(value: number) => [formatCurrency(value)]}
              contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }}
            />
            <Legend
              verticalAlign="bottom"
              height={36}
              formatter={(value: string) => (
                <span className="text-sm text-slate-600">{value}</span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default IncomeBreakdownPie;
