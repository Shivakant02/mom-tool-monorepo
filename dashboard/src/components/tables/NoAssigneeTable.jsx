export default function NoAssigneeTable({ tasks }) {
  const unassignedTasks = tasks.filter(
    (t) => !t.fields.assignee || t.fields.assignee.displayName === "System"
  );

  return (
    <div className="w-full md:w-1/2 p-2">
      <h2 className="text-lg font-semibold mb-2">No Assignee Tasks</h2>
      <div className="border border-base-300 rounded-md overflow-hidden">
        <table className="table table-fixed w-full">
          <thead className="bg-base-200 sticky top-0 z-10">
            <tr>
              <th className="w-1/2">Summary</th>
              <th className="w-1/2">Status</th>
            </tr>
          </thead>
        </table>
        <div className="max-h-45 overflow-y-auto">
          <table className="table table-fixed w-full">
            <tbody>
              {unassignedTasks.map((task) => (
                <tr key={task.id} className="hover">
                  <td className="w-1/2">{task.fields.summary}</td>
                  <td className="w-1/2">{task.fields.status.name}</td>
                </tr>
              ))}
              {unassignedTasks.length === 0 && (
                <tr>
                  <td colSpan="2" className="text-center">
                    All tasks assigned ✅
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
