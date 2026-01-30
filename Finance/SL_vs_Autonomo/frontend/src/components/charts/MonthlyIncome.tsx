import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, ReferenceLine } from "recharts";
import { ScenarioResult } from "../../api/simulator";

const MonthlyIncome = ({ data }: { data: Record<string, ScenarioResult | undefined> }) => {
  const chartData = Object.entries(data).map(([label, result]) => ({
    scenario: label,
    value: result?.renta_mensual_neta || 0,
  }));

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer>
        <BarChart data={chartData}>
          <XAxis dataKey="scenario" />
          <YAxis />
          <Tooltip />
          <Legend />
          <ReferenceLine y={2000} stroke="#ef4444" strokeDasharray="4 4" />
          <Bar dataKey="value" fill="#0ea5e9" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default MonthlyIncome;
