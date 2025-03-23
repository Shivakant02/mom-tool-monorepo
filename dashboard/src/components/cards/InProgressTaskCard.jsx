export default function InProgressTasksCard({ count }) {
  return (
    <div className="stat bg-base-100 rounded-xl shadow">
      <div className="stat-title">In Progress</div>
      <div className="stat-value text-info">{count}</div>
    </div>
  );
}
