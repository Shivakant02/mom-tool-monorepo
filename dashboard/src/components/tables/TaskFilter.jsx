export default function TaskFilter({ filter, setFilter }) {
  const filters = ["All", "To Do", "In Progress", "Done"];

  return (
    <div className="flex space-x-4 mb-4">
      {filters.map((f) => (
        <button
          key={f}
          className={`btn ${filter === f ? "btn-primary" : "btn-outline"}`}
          onClick={() => setFilter(f)}
        >
          {f}
        </button>
      ))}
    </div>
  );
}
