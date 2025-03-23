export default function OverdueTable({ tasks }) {
  const overdueTasks = tasks.filter((t) => {
    const dueDate = t.fields.duedate;
    return (
      dueDate &&
      new Date(dueDate) < new Date() &&
      t.fields.status.name !== "Done"
    );
  });

  return (
    <div className="w-full md:w-1/2 p-2">
      <h2 className="text-lg font-semibold mb-2">Overdue Tasks</h2>
      <div className="border border-base-300 rounded-md overflow-hidden">
        <table className="table table-fixed w-full">
          <thead className="bg-base-200 sticky top-0 z-10">
            <tr>
              <th className="w-1/2">Summary</th>
              <th className="w-1/2">Due Date</th>
            </tr>
          </thead>
        </table>
        <div className="max-h-45 overflow-y-auto">
          <table className="table table-fixed w-full">
            <tbody>
              {overdueTasks.map((task) => (
                <tr key={task.id} className="hover">
                  <td className="w-1/2">{task.fields.summary}</td>
                  <td className="w-1/2">{task.fields.duedate || "-"}</td>
                </tr>
              ))}
              {overdueTasks.length === 0 && (
                <tr>
                  <td colSpan="2" className="text-center">
                    No overdue tasks 🎉
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
