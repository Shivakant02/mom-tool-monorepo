// import { useState, useEffect } from "react";
// import axios from "axios";
// import MomEditor from "../components/mom/MomEditor";
// import MomActions from "../components/mom/MomActions";
// import { formatMomJson, parseMomText } from "./formatMomJson";

// const MOM_API = import.meta.env.VITE_MOM_API_BASE_URL;

// export default function MomPage() {
//   const [momText, setMomText] = useState("");
//   const [jsonData, setJsonData] = useState(null); // Ensure it's null initially

//   // Fetch MOM Data on Page Load
//   useEffect(() => {
//     const fetchMomData = async () => {
//       try {
//         const response = await axios.get(`${MOM_API}/process_meeting`);
//         console.log("Fetched MOM Data:", response.data);

//         setJsonData(response.data); // Set the entire data
//         setMomText(formatMomJson(response.data.mom_data)); // Set editable text
//       } catch (error) {
//         console.error("Error fetching MOM:", error);
//         alert("Failed to fetch MOM data.");
//       }
//     };

//     fetchMomData();
//   }, []); // Runs only on mount

//   // Function to handle Save (Convert Text -> JSON -> API Call)
//   const handleSave = async () => {
//     if (!jsonData) {
//       alert("No MOM data available to update.");
//       return;
//     }

//     // Convert edited text back into JSON format
//     const updatedMomData = parseMomText(momText);

//     // Update only `mom_data` while preserving `meeting_id` & `attendees`
//     const requestBody = {
//       meeting_id: jsonData.meeting_id, // Extract `meeting_id`
//       mom_data: updatedMomData, // Replace `mom_data`
//     };

//     console.log(requestBody);

//     try {
//       console.log("Updated MOM Payload:", requestBody);

//       const response = await axios.put(`${MOM_API}/update_mom`, requestBody, {
//         headers: { "Content-Type": "application/json" },
//       });

//       if (response.status === 200) {
//         alert("MOM saved successfully!");
//         setJsonData(requestBody); // Update local state with new data
//       }
//     } catch (error) {
//       console.error("Error saving MOM:", error);
//       alert("An error occurred while saving MOM.");
//     }
//   };

//   return (
//     <div className="p-6 space-y-4">
//       <h1 className="text-2xl font-bold mb-4">Meeting Minutes (MOM)</h1>
//       <button
//         onClick={handleSave}
//         className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
//       >
//         Save MOM
//       </button>
//       <MomEditor momText={momText} setMomText={setMomText} />
//       <MomActions momText={momText} />
//     </div>
//   );
// }

// import { useState, useEffect } from "react";
// import axios from "axios";
// import MomEditor from "../components/mom/MomEditor";
// import MomActions from "../components/mom/MomActions";
// import { formatMomJson, parseMomText } from "./formatMomJson";

// const MOM_API = import.meta.env.VITE_MOM_API_BASE_URL;

// export default function MomPage() {
//   const [momText, setMomText] = useState("");
//   const [jsonData, setJsonData] = useState(null); // Ensure it's null initially

//   // Fetch MOM Data on Page Load
//   useEffect(() => {
//     const fetchMomData = async () => {
//       try {
//         const response = await axios.get(`${MOM_API}/process_meeting`);
//         console.log("Fetched MOM Data:", response.data);

//         setJsonData(response.data); // Set the entire data
//         // Use the updated formatMomJson which checks for nested "mom_data"
//         setMomText(formatMomJson(response.data.mom_data));
//       } catch (error) {
//         console.error("Error fetching MOM:", error);
//         alert("Failed to fetch MOM data.");
//       }
//     };

//     fetchMomData();
//   }, []); // Runs only on mount

//   // Function to handle Save (Convert Text -> JSON -> API Call)
//   const handleSave = async () => {
//     if (!jsonData) {
//       alert("No MOM data available to update.");
//       return;
//     }

//     // Convert edited text back into JSON format
//     // const updatedMomData = parseMomText(momText);

//     // // Update only `mom_data` while preserving `meeting_id` & (if needed) `attendees`
//     // const requestBody = {
//     //   meeting_id: jsonData.meeting_id, // Extract `meeting_id`
//     //   mom_data: updatedMomData, // Replace `mom_data`
//     // };

//     // console.log("Updated MOM Payload:", requestBody);

//     const requestBody = {
//       meeting_id: jsonData.meeting_id,
//       attendees: jsonData.attendees,
//     };

//     try {
//       // const response = await axios.put(`${MOM_API}/update_mom`, requestBody, {
//       //   headers: { "Content-Type": "application/json" },
//       // });
//       const response = await axios.post(`${MOM_API}/send_mom`, requestBody, {
//         headers: { "Content-Type": "application/json" },
//       });

//       if (response.status === 200) {
//         alert("MOM saved successfully!");
//         setJsonData(requestBody);
//         // Update local state with new data
//       }
//     } catch (error) {
//       console.error("Error saving MOM:", error);
//       alert("An error occurred while saving MOM.");
//     }
//   };

//   return (
//     <div className="p-6 space-y-4">
//       <h1 className="text-2xl font-bold mb-4">Meeting Minutes (MOM)</h1>
//       <button
//         onClick={handleSave}
//         className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
//       >
//         Save MOM
//       </button>
//       <MomEditor momText={momText} setMomText={setMomText} />
//       <MomActions momText={momText} />
//     </div>
//   );
// }

import { useState, useEffect } from "react";
import axios from "axios";
import MomEditor from "../components/mom/MomEditor";
import MomActions from "../components/mom/MomActions";
import { formatMomJson, parseMomText } from "./formatMomJson";

const MOM_API = import.meta.env.VITE_MOM_API_BASE_URL;
const JIRA_API = import.meta.env.VITE_JIRA_API_BASE_URL;

/**
 * Transforms action items to the desired format:
 * { summary, description, assignee_email, due_date }
 */
function transformActionItems(actionItems = []) {
  return actionItems.map((item) => ({
    summary: item.item || "No Summary Provided",
    description: item.description || "",
    assignee_email: item.email || "",
    due_date: item.deadline || "",
  }));
}

export default function MomPage() {
  const [momText, setMomText] = useState("");
  const [jsonData, setJsonData] = useState(null); // Entire data from API

  // Fetch MOM Data on Page Load
  useEffect(() => {
    const fetchMomData = async () => {
      try {
        const response = await axios.get(`${MOM_API}/process_meeting`);
        console.log("Fetched MOM Data:", response.data);

        setJsonData(response.data); // Save the entire data
        // Use the updated formatMomJson which checks for nested "mom_data"
        setMomText(formatMomJson(response.data.mom_data));
      } catch (error) {
        console.error("Error fetching MOM:", error);
        alert("Failed to fetch MOM data.");
      }
    };

    fetchMomData();
  }, []); // Runs only on mount

  // Function to handle Save (Convert Text -> JSON -> API Call)
  const handleSave = async () => {
    if (!jsonData) {
      alert("No MOM data available to update.");
      return;
    }

    // Convert edited text back into JSON format
    const updatedMomData = parseMomText(momText);

    // Build request body for updating MOM if needed (here we focus on sending email and creating tasks)
    // Request body for sending MOM email: meeting_id and attendees
    const sendMomRequestBody = {
      meeting_id: jsonData.meeting_id,
      attendees: jsonData.attendees,
    };

    // Request body for creating tasks: an array of action items
    const createTasksRequestBody = transformActionItems(
      updatedMomData.mom_data.action_items
    );
    console.log(createTasksRequestBody);

    console.log("Send MOM Payload:", sendMomRequestBody);
    console.log("Create Tasks Payload:", createTasksRequestBody);

    try {
      // Execute both API calls in parallel
      const [sendResponse, createResponse] = await Promise.all([
        axios.post(`${MOM_API}/send_mom`, sendMomRequestBody, {
          headers: { "Content-Type": "application/json" },
        }),
        axios.post(`${JIRA_API}/api/v1/create-tasks`, createTasksRequestBody, {
          headers: { "Content-Type": "application/json" },
        }),
      ]);

      if (sendResponse.status === 200 && createResponse.status === 200) {
        alert("MOM saved, email sent, and tasks created successfully!");
        // Optionally update local state; here we update jsonData with meeting_id and attendees if needed.
        setJsonData({
          meeting_id: jsonData.meeting_id,
          attendees: jsonData.attendees,
          mom_data: updatedMomData,
        });
      }
    } catch (error) {
      console.error(
        "Error in saving MOM, sending email, or creating tasks:",
        error
      );
      alert("An error occurred while saving MOM.");
    }
  };

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold mb-4">Meeting Minutes (MOM)</h1>
      <button
        onClick={handleSave}
        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        Save MOM
      </button>
      <MomEditor momText={momText} setMomText={setMomText} />
      <MomActions momText={momText} />
    </div>
  );
}
