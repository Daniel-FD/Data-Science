import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { ScenarioResult } from "../../api/simulator";

const COLORS = ["#0ea5e9", "#22c55e", "#f59e0b", "#ef4444"];

const TaxComposition = ({ result }: { result?: ScenarioResult }) => {
  const data = result
    ? Object.entries(result.tax_breakdown).map(([name, value]) => ({ name, value }))
    : [];

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer>
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" outerRadius={80} label>
            {data.map((_, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TaxComposition;
