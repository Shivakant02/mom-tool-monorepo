export default function TotalTasksCard({ count }) {
  return (
    <div className="stat bg-base-100 rounded-xl shadow">
      <div className="stat-title">Total Tasks</div>
      <div className="stat-value text-primary">{count}</div>
    </div>
  );
}
