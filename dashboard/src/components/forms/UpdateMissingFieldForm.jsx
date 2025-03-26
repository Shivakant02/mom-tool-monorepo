import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";

export default function UpdateMissingFieldsForm({ issueKey }) {
  const navigate = useNavigate();
  const location = useLocation();
  const existingTask = location.state?.task || {}; // Get passed task data

  // Helper function to ensure correct date format
  const formatDate = (dateString) => {
    if (!dateString) return "";
    return new Date(dateString).toISOString().split("T")[0]; // Convert to YYYY-MM-DD
  };

  const [formData, setFormData] = useState({
    summary: existingTask.fields?.summary || "",
    duedate: formatDate(existingTask.fields?.duedate),
  });

  useEffect(() => {
    if (!existingTask.fields) {
      // If no data was passed, fetch the task details from API
      const fetchTaskDetails = async () => {
        try {
          const apiUrl = `${
            import.meta.env.VITE_JIRA_API_BASE_URL
          }/api/v1/task/${issueKey}`;
          const response = await axios.get(apiUrl);

          if (response.status === 200) {
            const { summary, duedate, assignee, description } =
              response.data.fields;
            setFormData({
              summary: summary || "",
              duedate: formatDate(duedate),
              assignee: assignee?.emailAddress || "",
              description: description || "",
            });
          }
        } catch (error) {
          console.error("Error fetching task details:", error);
        }
      };
      fetchTaskDetails();
    }
  }, [issueKey, existingTask]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const apiUrl = `${
      import.meta.env.VITE_JIRA_API_BASE_URL
    }/api/v1/update-missing-fields/${issueKey}`;

    try {
      const response = await axios.post(apiUrl, {
        fieldsToUpdate: formData,
      });

      if (response.status === 200) {
        alert("Task updated successfully!");
        navigate("/tasks-list"); // Redirect to task list
      } else {
        alert("Failed to update task");
      }
    } catch (error) {
      console.error("Error updating task:", error);
      alert("Error updating task");
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 bg-white p-4 rounded-md shadow  "
    >
      <div>
        <label className="block text-sm font-medium mb-3">Summary</label>
        <input
          type="text"
          name="summary"
          value={formData.summary}
          onChange={handleChange}
          className="input input-bordered w-full"
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-3">Due Date</label>
        <input
          type="date"
          name="duedate"
          value={formData.duedate}
          onChange={handleChange}
          className="input input-bordered w-full"
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-3">Assignee Email</label>
        <input
          type="email"
          name="assignee"
          value={formData.assignee}
          onChange={handleChange}
          className="input input-bordered w-full"
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-3">Description</label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          className="textarea textarea-bordered w-full"
        />
      </div>
      <button type="submit" className="btn btn-primary w-full">
        Update Task
      </button>
    </form>
  );
}
