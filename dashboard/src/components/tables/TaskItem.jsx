// src/components/tasks/TaskRow.jsx
export default function TaskItem({ task }) {
  const { summary, status, assignee, duedate } = task.fields;
  const dueSoon = duedate && new Date(duedate) < new Date();

  return (
    <tr>
      <td>{summary}</td>
      <td>{status.name}</td>
      <td>{assignee ? assignee.displayName : "Unassigned"}</td>
      <td className={`${dueSoon ? "text-red-500 font-semibold" : ""}`}>
        {duedate || "No due date"}
      </td>
    </tr>
  );
}
