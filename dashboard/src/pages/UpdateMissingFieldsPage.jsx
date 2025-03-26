import { useParams } from "react-router-dom";
import UpdateMissingFieldsForm from "../components/forms/UpdateMissingFieldForm";

export default function UpdateMissingFieldsPage() {
  const { issueKey } = useParams();

  return (
    <div className="p-4 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Update Missing Fields</h1>
      <UpdateMissingFieldsForm issueKey={issueKey} />
    </div>
  );
}
