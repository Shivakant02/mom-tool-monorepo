export default function DoneTasksCard({ count }) {
  return (
    <div className="stat bg-base-100 rounded-xl shadow">
      <div className="stat-title">Done</div>
      <div className="stat-value text-success">{count}</div>
    </div>
  );
}
