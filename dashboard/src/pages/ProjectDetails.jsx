// src/pages/ProjectDetails.jsx
import { useEffect, useState } from "react";
import { fetchProjectDetails } from "../services/JiraApi";
import ProjectInfoCard from "../components/project/ProjectInfoCard";
import IssueTypesCard from "../components/project/IssueTypesCard";

export default function ProjectDetails() {
  const [project, setProject] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      const data = await fetchProjectDetails("CPG"); // replace "CPG" with dynamic id if needed
      setProject(data);
    };
    fetchData();
  }, []);

  if (!project)
    return <p className="text-center p-10">Loading project details...</p>;

  return (
    <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
      <ProjectInfoCard project={project} />
      <IssueTypesCard issueTypes={project.issueTypes} />
    </div>
  );
}
