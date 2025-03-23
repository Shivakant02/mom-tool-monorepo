// src/components/project/IssueTypesCard.jsx
export default function IssueTypesCard({ issueTypes }) {
  return (
    <div className="bg-base-100 shadow-xl rounded-xl p-5">
      <h3 className="text-lg font-semibold mb-4">Supported Issue Types</h3>
      <ul className="space-y-2">
        {issueTypes.map((type) => (
          <li
            key={type.id}
            className="flex items-center gap-2 text-sm bg-base-200 p-2 rounded"
          >
            <span className="font-medium">{type.name}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
