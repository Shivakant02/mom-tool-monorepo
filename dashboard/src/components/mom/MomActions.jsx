// src/components/mom/MomActions.jsx
import { sendMomToAssignees } from "../../services/MomService";

export default function MomActions({ momText }) {
  const handleSend = async () => {
    await sendMomToAssignees(momText);
    alert("MOM sent to all assignees!");
  };

  return (
    <div className="flex justify-end space-x-2">
      <button className="btn btn-primary" onClick={handleSend}>
        Send MOM to Assignees
      </button>
    </div>
  );
}
