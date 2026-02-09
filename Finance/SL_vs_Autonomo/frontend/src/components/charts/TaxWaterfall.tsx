import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { ScenarioResult } from "../../api/simulator";

const TaxWaterfall = ({ data }: { data: Record<string, ScenarioResult | undefined> }) => {
  const chartData = Object.entries(data).map(([label, result]) => ({
    scenario: label,
    impuestos: result?.impuestos_rescate || 0,
    capital: result?.capital_neto || 0,
  }));

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer>
        <BarChart data={chartData}>
          <XAxis dataKey="scenario" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="impuestos" stackId="a" fill="#ef4444" />
          <Bar dataKey="capital" stackId="a" fill="#22c55e" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TaxWaterfall;
