import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { OptimalSalaryPoint } from "../../api/simulator";

const OptimalSalary = ({ data }: { data: OptimalSalaryPoint[] }) => {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer>
        <LineChart data={data}>
          <XAxis dataKey="salario" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="renta_mensual_neta" stroke="#14b8a6" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default OptimalSalary;
