import { useState } from "react";

export default function OverdueTable({ tasks, sendReminder }) {
  const [selectedTasks, setSelectedTasks] = useState([]);

  const overdueTasks = tasks.filter((t) => {
    const dueDate = t.fields.duedate;
    return (
      dueDate &&
      new Date(dueDate) < new Date() &&
      t.fields.status.name !== "Done"
    );
  });

  const toggleTaskSelection = (taskKey) => {
    setSelectedTasks((prevSelected) =>
      prevSelected.includes(taskKey)
        ? prevSelected.filter((key) => key !== taskKey)
        : [...prevSelected, taskKey]
    );
  };

  const toggleSelectAll = () => {
    setSelectedTasks(
      selectedTasks.length === overdueTasks.length
        ? []
        : overdueTasks.map((task) => task.key)
    );
  };

  const handleSendSingleReminder = (taskKey) => {
    sendReminder([taskKey]); // Wraps single ID in array
  };

  const handleSendAll = () => {
    if (selectedTasks.length > 0) {
      sendReminder(selectedTasks); // Sends all selected tasks
    }
  };

  return (
    <div className="w-full p-4">
      <h2 className="text-lg font-semibold mb-4 flex items-center">
        <span className="text-red-500 text-xl">📌</span>
        <span className="ml-2">Overdue Tasks</span>
      </h2>

      <div className="border border-base-300 rounded-md shadow-lg overflow-hidden">
        <div className="relative">
          <table className="table w-full border-collapse">
            <thead className="bg-base-200 sticky top-0 z-10">
              <tr className="text-left">
                <th className="w-10 px-4 py-3">
                  <input
                    type="checkbox"
                    onChange={toggleSelectAll}
                    checked={selectedTasks.length === overdueTasks.length}
                    className="checkbox"
                  />
                </th>
                <th className="w-1/6 px-4 py-3">Task ID</th>
                <th className="w-2/5 px-4 py-3">Summary</th>
                <th className="w-1/6 px-4 py-3">Assignee</th>
                <th className="w-1/6 px-4 py-3">Due Date</th>
                <th className="w-1/6 px-4 py-3 text-center">Remind</th>
              </tr>
            </thead>
          </table>

          <div className="max-h-60 overflow-y-auto">
            <table className="table w-full border-collapse">
              <tbody>
                {overdueTasks.length > 0 ? (
                  overdueTasks.map((task) => (
                    <tr key={task.id} className="hover:bg-gray-100">
                      <td className="w-10 px-4 py-3">
                        <input
                          type="checkbox"
                          checked={selectedTasks.includes(task.key)}
                          onChange={() => toggleTaskSelection(task.key)}
                          className="checkbox"
                        />
                      </td>
                      <td className="w-1/6 px-4 py-3 font-medium">
                        {task.key}
                      </td>
                      <td className="w-2/6 px-4 py-3 truncate">
                        {task.fields.summary}
                      </td>
                      <td className="w-1/6 px-4 py-3 text-left whitespace-nowrap">
                        {task.fields.assignee?.displayName ? (
                          <div className="flex items-center">
                            <span className="font-medium">
                              {task.fields.assignee.displayName}
                            </span>
                          </div>
                        ) : (
                          <span className="text-red-500 font-medium">
                            Unassigned
                          </span>
                        )}
                      </td>
                      <td className="w-1/6 px-4 py-3 text-red-500">
                        {task.fields.duedate || "-"}
                      </td>
                      <td className="w-1/6 px-4 py-3 text-center">
                        <button
                          onClick={() => handleSendSingleReminder(task.key)}
                          className="btn btn-sm btn-outline btn-primary"
                        >
                          Remind
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6" className="p-4 text-center text-gray-500">
                      🎉 No overdue tasks!
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="flex justify-end mt-4">
        <button
          onClick={handleSendAll}
          disabled={selectedTasks.length === 0}
          className={`btn btn-primary ${
            selectedTasks.length === 0 ? "btn-disabled" : ""
          }`}
        >
          Remind All
        </button>
      </div>
    </div>
  );
}
