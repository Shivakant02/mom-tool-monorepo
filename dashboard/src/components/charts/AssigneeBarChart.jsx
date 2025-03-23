// src/components/charts/AssigneeBarChart.jsx
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

const AssigneeBarChart = ({ data }) => {
  return (
    <div className="card bg-base-100 shadow-xl p-4 w-full md:w-1/2">
      <h2 className="text-lg font-bold mb-4">Tasks per Assignee</h2>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="assignee" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="tasks" fill="#60a5fa" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AssigneeBarChart;
