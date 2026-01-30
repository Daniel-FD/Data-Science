import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const EffectiveTaxRate = ({ data }: { data: Array<{ income: number; rate: number }> }) => {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer>
        <LineChart data={data}>
          <XAxis dataKey="income" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="rate" stroke="#0ea5e9" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default EffectiveTaxRate;
