import { useState } from "react";
import { useNavigate } from "react-router-dom"; // Assuming React Router is used

export default function MissingFieldsPage({ tasks }) {
  const [missingFilter, setMissingFilter] = useState(""); // No default filter
  const navigate = useNavigate();

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
    return true; // Show all if no filter is selected
  });

  return (
    <div className="w-full p-4 space-y-3">
      <h2 className="text-lg font-semibold">Missing Field Tasks</h2>

      {/* Dropdown for selecting missing fields */}
      <div className="dropdown">
        <label tabIndex={0} className="btn btn-outline">
          {missingFilter ? `Filter: ${missingFilter}` : "Select Filter"}
        </label>
        <ul
          tabIndex={0}
          className="dropdown-content z-[1] menu p-2 shadow bg-base-200 rounded-box w-52"
        >
          <li>
            <a
              onClick={() => {
                setMissingFilter("Assignee");
                document.activeElement?.blur(); // Close dropdown
              }}
            >
              Missing Assignee
            </a>
          </li>
          <li>
            <a
              onClick={() => {
                setMissingFilter("Summary");
                document.activeElement?.blur(); // Close dropdown
              }}
            >
              Missing Summary
            </a>
          </li>
          <li>
            <a
              onClick={() => {
                setMissingFilter("Due Date");
                document.activeElement?.blur(); // Close dropdown
              }}
            >
              Missing Due Date
            </a>
          </li>
          <li>
            <a
              onClick={() => {
                setMissingFilter("");
                document.activeElement?.blur(); // Close dropdown
              }}
            >
              Show All
            </a>
          </li>
        </ul>
      </div>

      {/* Table for displaying missing fields */}
      <div className="border border-base-300 rounded-md overflow-hidden">
        <table className="table table-fixed w-full">
          <thead className="bg-base-200 sticky top-0 z-10">
            <tr>
              <th className="w-1/5">Task ID</th>
              <th className="w-1/5">Summary</th>
              <th className="w-1/5">Status</th>
              <th className="w-1/5">Due Date</th>
              <th className="w-1/5">Assignee</th> {/* New column added */}
            </tr>
          </thead>
        </table>
        <div className="max-h-80 overflow-y-auto">
          <table className="table table-fixed w-full">
            <tbody>
              {filteredTasks.map((task) => (
                <tr key={task.id} className="hover">
                  <td
                    className="w-1/5 text-blue-500 cursor-pointer"
                    onClick={() =>
                      navigate(`/update-missing-fields/${task.key}`, {
                        state: { task },
                      })
                    }
                  >
                    {task.key}
                  </td>
                  <td className="w-1/5">{task.fields.summary || "-"}</td>
                  <td className="w-1/5">{task.fields.status.name}</td>
                  <td className="w-1/5">{task.fields.duedate || "-"}</td>
                  <td className="w-1/5">
                    {task.fields.assignee?.displayName || "Unassigned"}
                  </td>
                </tr>
              ))}
              {filteredTasks.length === 0 && (
                <tr>
                  <td colSpan="5" className="text-center">
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
