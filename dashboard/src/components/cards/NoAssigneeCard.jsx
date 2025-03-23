export default function NoAssigneeCard({ count }) {
  return (
    <div className="stat bg-base-100 rounded-xl shadow">
      <div className="stat-title">No Assignee(system)</div>
      <div className="stat-value text-error">{count}</div>
    </div>
  );
}
