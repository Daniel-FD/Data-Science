import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { ScenarioResult } from "../../api/simulator";

const CapitalEvolution = ({ data }: { data: Record<string, ScenarioResult | undefined> }) => {
  const years = data[Object.keys(data)[0]]?.historial.map((h) => h.año) || [];
  const chartData = years.map((year, idx) => ({
    year,
    ...Object.fromEntries(
      Object.entries(data).map(([label, result]) => [label, result?.historial[idx]?.capital_acumulado || 0])
    ),
  }));

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer>
        <LineChart data={chartData}>
          <XAxis dataKey="year" />
          <YAxis />
          <Tooltip />
          <Legend />
          {Object.keys(data).map((label) => (
            <Line key={label} type="monotone" dataKey={label} strokeWidth={2} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CapitalEvolution;
