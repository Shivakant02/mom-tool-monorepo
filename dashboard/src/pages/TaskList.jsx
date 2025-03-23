// src/pages/TaskList.jsx
import { useEffect, useState } from "react";
import { fetchTasks } from "../services/JiraApi";
import TaskFilter from "../components/tables/TaskFilter";
import TaskItem from "../components/tables/TaskItem";
import Pagination from "../components/tables/Pagination";

export default function TaskList() {
  const [tasks, setTasks] = useState([]);
  const [filter, setFilter] = useState("All");
  const [currentPage, setCurrentPage] = useState(1);
  const tasksPerPage = 5;

  useEffect(() => {
    const getTasks = async () => {
      const data = await fetchTasks();
      setTasks(data);
    };
    getTasks();
  }, []);

  const filteredTasks =
    filter === "All"
      ? tasks
      : tasks.filter((t) => t.fields.status.name === filter);

  const totalPages = Math.ceil(filteredTasks.length / tasksPerPage);
  const indexOfLastTask = currentPage * tasksPerPage;
  const indexOfFirstTask = indexOfLastTask - tasksPerPage;
  const currentTasks = filteredTasks.slice(indexOfFirstTask, indexOfLastTask);

  useEffect(() => {
    // Reset to page 1 when filter changes
    setCurrentPage(1);
  }, [filter]);

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-bold mb-4">Task List</h1>
      <TaskFilter filter={filter} setFilter={setFilter} />
      <div className="overflow-x-auto">
        <table className="table w-full table-fixed border border-base-300">
          <thead>
            <tr>
              <th className="w-1/3">Summary</th>
              <th className="w-1/6">Status</th>
              <th className="w-1/4">Assignee</th>
              <th className="w-1/4">Due Date</th>
            </tr>
          </thead>
          <tbody>
            {currentTasks.map((task) => (
              <TaskItem key={task.id} task={task} />
            ))}
          </tbody>
        </table>
      </div>

      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        setCurrentPage={setCurrentPage}
      />
    </div>
  );
}
