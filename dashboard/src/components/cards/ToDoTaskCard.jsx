export default function ToDoTasksCard({ count }) {
  return (
    <div className="stat bg-base-100 rounded-xl shadow">
      <div className="stat-title">To Do</div>
      <div className="stat-value text-warning">{count}</div>
    </div>
  );
}
