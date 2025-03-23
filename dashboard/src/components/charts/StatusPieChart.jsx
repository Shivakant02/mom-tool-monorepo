import {
  PieChart,
  Pie,
  Cell,
  Legend,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const COLORS = ["#60a5fa", "#facc15", "#4ade80"];

const StatusPieChart = ({ data }) => {
  const chartData = [
    { name: "To Do", value: data.todo },
    { name: "In Progress", value: data.inProgress },
    { name: "Done", value: data.done },
  ];

  return (
    <div className="card bg-base-100 shadow-xl p-4 w-full md:w-1/2">
      <h2 className="text-lg font-bold mb-4">Tasks by Status</h2>
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={chartData}
            dataKey="value"
            nameKey="name"
            outerRadius={80}
            label
          >
            {chartData.map((entry, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default StatusPieChart;
