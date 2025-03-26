import React, { useEffect, useState } from "react";
import { fetchTasks } from "../services/JiraApi";
import MissingFieldsPage from "../components/tables/NoAssigneeTable";

function MissingTable() {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    const getTasks = async () => {
      const data = await fetchTasks();
      setTasks(data);
    };
    getTasks();
  }, []);
  return (
    <div>
      <MissingFieldsPage tasks={tasks} />
    </div>
  );
}

export default MissingTable;
