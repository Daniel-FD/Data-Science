import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts";

const CrossoverPoint = ({ data }: { data: Array<Record<string, number>> }) => {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer>
        <LineChart data={data}>
          <XAxis dataKey="facturacion" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="autonomo" stroke="#0ea5e9" />
          <Line type="monotone" dataKey="sl_retencion" stroke="#22c55e" />
          <Line type="monotone" dataKey="sl_dividendos" stroke="#f59e0b" />
          <Line type="monotone" dataKey="sl_mixto" stroke="#ef4444" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CrossoverPoint;
