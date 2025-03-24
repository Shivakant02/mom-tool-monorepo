import { useState } from "react";

export default function TaskFilter({ filter, setFilter, assignees }) {
  const [statusSearch, setStatusSearch] = useState("");
  const [assigneeSearch, setAssigneeSearch] = useState("");
  const [openStatus, setOpenStatus] = useState(false);
  const [openAssignee, setOpenAssignee] = useState(false);

  const statusOptions = ["To Do", "In Progress", "Done"];

  const handleStatusChange = (value) => {
    setFilter((prev) => ({ ...prev, status: value }));
    setOpenStatus(false);
    setStatusSearch("");
  };

  const handleAssigneeChange = (value) => {
    setFilter((prev) => ({ ...prev, assignee: value }));
    setOpenAssignee(false);
    setAssigneeSearch("");
  };

  const handleDateChange = (type, value) => {
    setFilter((prev) => ({ ...prev, [type]: value }));
  };

  const handleClearFilters = () => {
    setFilter({ status: "", assignee: "", startDate: "", endDate: "" });
    setStatusSearch("");
    setAssigneeSearch("");
    setOpenStatus(false);
    setOpenAssignee(false);
  };

  return (
    <div className="flex flex-wrap gap-4 mb-6 items-end">
      {/* Status Dropdown */}
      <div className="relative">
        <button
          type="button"
          className="btn btn-outline w-48 justify-between"
          onClick={() => {
            setOpenStatus(!openStatus);
            setOpenAssignee(false);
          }}
        >
          {filter.status || "Select Status"}
        </button>
        {openStatus && (
          <div className="absolute mt-1 bg-base-200 p-4 rounded-box w-64 space-y-2 z-20">
            <input
              type="text"
              placeholder="Search status..."
              value={statusSearch}
              onChange={(e) => setStatusSearch(e.target.value)}
              className="input input-bordered w-full"
            />
            <ul className="menu p-0 space-y-1">
              <li>
                <a onClick={() => handleStatusChange("")}>All Status</a>
              </li>
              {statusOptions
                .filter((s) =>
                  s.toLowerCase().includes(statusSearch.toLowerCase())
                )
                .map((status) => (
                  <li key={status}>
                    <a onClick={() => handleStatusChange(status)}>{status}</a>
                  </li>
                ))}
            </ul>
          </div>
        )}
      </div>

      {/* Assignee Dropdown */}
      <div className="relative">
        <button
          type="button"
          className="btn btn-outline w-48 justify-between"
          onClick={() => {
            setOpenAssignee(!openAssignee);
            setOpenStatus(false);
          }}
        >
          {filter.assignee || "Select Assignee"}
        </button>
        {openAssignee && (
          <div className="absolute mt-1 bg-base-200 p-4 rounded-box w-64 space-y-2 z-20">
            <input
              type="text"
              placeholder="Search assignee..."
              value={assigneeSearch}
              onChange={(e) => setAssigneeSearch(e.target.value)}
              className="input input-bordered w-full"
            />
            <ul className="menu p-0 space-y-1 max-h-48 overflow-y-auto">
              <li>
                <a onClick={() => handleAssigneeChange("")}>All Assignees</a>
              </li>
              {assignees
                .filter((a) =>
                  a.toLowerCase().includes(assigneeSearch.toLowerCase())
                )
                .map((person) => (
                  <li key={person}>
                    <a onClick={() => handleAssigneeChange(person)}>{person}</a>
                  </li>
                ))}
            </ul>
          </div>
        )}
      </div>

      {/* Date Range Inline */}
      <div className="flex items-center gap-2">
        <div className="flex flex-col">
          <label className="text-xs">From</label>
          <input
            type="date"
            className="input input-bordered"
            value={filter.startDate || ""}
            onChange={(e) => handleDateChange("startDate", e.target.value)}
          />
        </div>
        <div className="flex flex-col">
          <label className="text-xs">To</label>
          <input
            type="date"
            className="input input-bordered"
            value={filter.endDate || ""}
            onChange={(e) => handleDateChange("endDate", e.target.value)}
          />
        </div>
      </div>

      {/* Clear Filters Button */}
      <button className="btn btn-error" onClick={handleClearFilters}>
        Clear All Filters
      </button>
    </div>
  );
}
