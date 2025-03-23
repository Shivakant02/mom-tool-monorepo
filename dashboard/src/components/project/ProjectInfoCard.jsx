// src/components/project/ProjectInfoCard.jsx
export default function ProjectInfoCard({ project }) {
  return (
    <div className="bg-base-100 shadow-xl rounded-xl p-5 space-y-4">
      <div className="flex items-center gap-4">
        <img
          src={project.avatarUrls["48x48"]}
          alt="avatar"
          className="rounded-full w-12 h-12"
        />
        <div>
          <h2 className="text-xl font-bold">{project.name}</h2>
          <p className="text-sm text-gray-500">
            Key: {project.key} | ID: {project.id}
          </p>
        </div>
      </div>
      <p className="text-sm">
        {project.description || "No description provided."}
      </p>
      <p className="badge badge-outline">Type: {project.projectTypeKey}</p>
      <p>
        Lead: <strong>{project.lead.displayName}</strong>
      </p>
      <a
        href={`https://lumiq-team-s5qytjpk.atlassian.net/jira/software/projects/CPG${project.key}/boards/1`}
        target="_blank"
        rel="noopener noreferrer"
        className="btn btn-primary btn-sm mt-2"
      >
        View in Jira
      </a>
    </div>
  );
}
