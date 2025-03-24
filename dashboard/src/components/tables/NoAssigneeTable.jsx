import { useState } from "react";

export default function NoAssigneeTable({ tasks }) {
  const [missingFilter, setMissingFilter] = useState("Assignee");

  // Filter logic based on missing field
  const filteredTasks = tasks.filter((t) => {
    if (missingFilter === "Assignee") {
      return !t.fields.assignee || t.fields.assignee.displayName === "System";
    } else if (missingFilter === "Summary") {
      return (
        !t.fields.summary || t.fields.summary.trim() === "No Summary Provided"
      );
    } else if (missingFilter === "Due Date") {
      return !t.fields.duedate || t.fields.duedate.trim() === "";
    }
    return false;
  });

  return (
    <div className="w-full md:w-1/2 p-2 space-y-3">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold">Missing Field Tasks</h2>
        <div className="dropdown">
          <label tabIndex={0} className="btn btn-outline">
            Filter: {missingFilter}
          </label>
          <ul
            tabIndex={0}
            className="dropdown-content z-[1] menu p-2 shadow bg-base-200 rounded-box w-52"
          >
            <li>
              <a onClick={() => setMissingFilter("Assignee")}>
                Missing Assignee
              </a>
            </li>
            <li>
              <a onClick={() => setMissingFilter("Summary")}>Missing Summary</a>
            </li>
            <li>
              <a onClick={() => setMissingFilter("Due Date")}>
                Missing Due Date
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div className="border border-base-300 rounded-md overflow-hidden">
        <table className="table table-fixed w-full">
          <thead className="bg-base-200 sticky top-0 z-10">
            <tr>
              <th className="w-1/4">Task ID</th>
              <th className="w-1/4">Summary</th>
              <th className="w-1/4">Status</th>
              <th className="w-1/4">Due Date</th>
            </tr>
          </thead>
        </table>
        <div className="max-h-45 overflow-y-auto">
          <table className="table table-fixed w-full">
            <tbody>
              {filteredTasks.map((task) => (
                <tr key={task.id} className="hover">
                  <td className="w-1/4">{task.key}</td>
                  <td className="w-1/4">{task.fields.summary || "-"}</td>
                  <td className="w-1/4">{task.fields.status.name}</td>
                  <td className="w-1/4">{task.fields.duedate || "-"}</td>
                </tr>
              ))}
              {filteredTasks.length === 0 && (
                <tr>
                  <td colSpan="4" className="text-center">
                    No tasks with missing {missingFilter.toLowerCase()} ✅
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
