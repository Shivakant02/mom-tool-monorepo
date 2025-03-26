// src/pages/Charts.jsx
import { useEffect, useState } from "react";
import { fetchTasks } from "../services/JiraApi";

// Stat Cards
import TotalTasksCard from "../components/cards/TotalTaskCard";
import ToDoTasksCard from "../components/cards/ToDoTaskCard";
import InProgressTasksCard from "../components/cards/InProgressTaskCard";
import DoneTasksCard from "../components/cards/DoneTaskCard";
import NoAssigneeCard from "../components/cards/NoAssigneeCard";

// Charts
import StatusPieChart from "../components/charts/StatusPieChart";
import AssigneeBarChart from "../components/charts/AssigneeBarChart";
import DueTrendLineChart from "../components/charts/DueTrendLineChart";
import OverdueTable from "../components/tables/OverdueTable";
// import NoAssigneeTable from "../components/tables/NoAssigneeTable";
import { sendReminder } from "../services/Email-automation";

export default function Charts() {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    const getTasks = async () => {
      const data = await fetchTasks();
      setTasks(data);
    };
    getTasks();
  }, []);

  const getCount = (status) =>
    tasks.filter((task) => task.fields.status.name === status).length;
  const noAssigneeCount = tasks.filter(
    (task) =>
      !task.fields.assignee || task.fields.assignee.displayName === "System"
  ).length;

  // Prepare Pie Chart Data
  const statusData = {
    todo: getCount("To Do"),
    inProgress: getCount("In Progress"),
    done: getCount("Done"),
  };

  // Prepare Bar Chart Data
  const assigneeMap = {};
  tasks.forEach((task) => {
    const assignee = task.fields.assignee
      ? task.fields.assignee.displayName
      : "Unassigned";
    assigneeMap[assignee] = (assigneeMap[assignee] || 0) + 1;
  });

  const assigneeData = Object.entries(assigneeMap).map(([assignee, tasks]) => ({
    assignee,
    tasks,
  }));

  // Prepare Line Chart Data: Count tasks due per date
  const dueDateMap = {};
  tasks.forEach((task) => {
    if (task.fields.duedate) {
      const date = task.fields.duedate;
      dueDateMap[date] = (dueDateMap[date] || 0) + 1;
    }
  });

  const dueTrendData = Object.entries(dueDateMap)
    .sort(([a], [b]) => new Date(a) - new Date(b))
    .map(([date, tasks]) => ({
      date,
      tasks,
    }));

  return (
    <div className="space-y-6 p-4">
      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <TotalTasksCard count={tasks.length} />
        <ToDoTasksCard count={getCount("To Do")} />
        <InProgressTasksCard count={getCount("In Progress")} />
        <DoneTasksCard count={getCount("Done")} />
        <NoAssigneeCard count={noAssigneeCount} />
      </div>

      {/* Charts Section */}
      <div className="flex flex-col md:flex-row gap-6">
        <StatusPieChart data={statusData} />
        <AssigneeBarChart data={assigneeData} />
      </div>
      <DueTrendLineChart data={dueTrendData} />

      {/* Bottom Section */}
      <div className="flex flex-col md:flex-row gap-4 mt-8">
        <OverdueTable tasks={tasks} sendReminder={sendReminder} />
      </div>
    </div>
  );
}
