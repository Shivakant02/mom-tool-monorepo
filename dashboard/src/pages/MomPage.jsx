import { useState, useEffect } from "react";
import axios from "axios";
import MomEditor from "../components/mom/MomEditor";
import { formatMomJson, parseMomText } from "./formatMomJson";
import {
  ChevronDown,
  Search,
  CalendarPlus,
  Sparkles,
  Send,
} from "lucide-react";
import FollowUpMeetingModal from "../components/modal/FollowUpMeetingModel";
import { scheduleMeeting } from "../services/scheduleMeeting";

const MOM_API = import.meta.env.VITE_MOM_API_BASE_URL;
const JIRA_API = import.meta.env.VITE_JIRA_API_BASE_URL;

// Transform action items for API
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
  const [meetings, setMeetings] = useState([]);
  const [selectedMeeting, setSelectedMeeting] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [aiSummary, setAiSummary] = useState(""); // AI summary state
  const [loadingSummary, setLoadingSummary] = useState(false); // Loading state for AI summary
  const [showModal, setShowModal] = useState(false);

  // Fetch MOM Data on Page Load
  useEffect(() => {
    const fetchMomData = async () => {
      try {
        const response = await axios.get(`${JIRA_API}/api/v1/mom`);
        console.log("Fetched MOM Data:", response.data);
        setMeetings(response.data);
      } catch (error) {
        console.error("Error fetching MOM:", error);
        alert("Failed to fetch MOM data.");
      }
    };

    fetchMomData();
  }, []);

  // Handle Meeting Selection
  const handleMeetingSelect = (meetingId) => {
    const selected = meetings.find((m) => m.meeting_id === meetingId);
    if (selected) {
      setSelectedMeeting(selected);
      setMomText(formatMomJson(selected.mom_data));
      setAiSummary(""); // Reset AI summary when switching meetings
    }
  };

  // Handle AI Summary Generation
  const handleGenerateSummary = async () => {
    if (!selectedMeeting) {
      alert("Please select a meeting first.");
      return;
    }

    setLoadingSummary(true);
    try {
      const response = await axios.post(
        `${JIRA_API}/api/v1/gemini/generate-summary`,
        {
          ...selectedMeeting.mom_data,
        }
      );

      // console.log(response);

      if (response.status === 200) {
        setAiSummary(response.data.summary);
      } else {
        alert("Failed to generate AI summary.");
      }
    } catch (error) {
      console.error("Error generating AI summary:", error);
      alert("An error occurred while generating the summary.");
    } finally {
      setLoadingSummary(false);
    }
  };

  // Handle Save (Convert Text -> JSON -> API Call)
  const handleSave = async () => {
    if (!selectedMeeting) {
      alert("Please select a meeting.");
      return;
    }

    const updatedMomData = parseMomText(momText);
    const sendMomRequestBody = {
      meeting_id: selectedMeeting.meeting_id,
      attendees: selectedMeeting.attendees,
    };
    const createTasksRequestBody = transformActionItems(
      updatedMomData.mom_data.action_items
    );

    console.log("Send MOM Payload:", sendMomRequestBody);
    console.log("Create Tasks Payload:", createTasksRequestBody);

    try {
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
      }
    } catch (error) {
      console.error("Error saving MOM:", error);
      alert("An error occurred while saving MOM.");
    }
  };

  return (
    <div className="p-6 space-y-4">
      {/* Title */}
      <h1 className="text-2xl font-bold text-gray-800">
        Meeting Minutes (MOM)
      </h1>

      {/* Search, Filter & Buttons Row */}
      <div className="flex justify-between items-center">
        {/* Left: Search & Meeting Filter */}
        <div className="flex gap-2 items-center">
          {/* Search Bar */}
          <div className="relative w-72">
            <Search className="absolute left-3 top-3 text-gray-500 w-5 h-5" />
            <input
              type="text"
              placeholder="Search meetings..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border rounded-lg text-sm focus:ring focus:ring-blue-300"
            />
          </div>

          {/* Meeting Dropdown */}
          <div className="relative w-80">
            <select
              className="w-full py-2 px-3 border rounded-lg text-sm bg-white shadow-sm focus:ring focus:ring-blue-300 appearance-none"
              onChange={(e) => handleMeetingSelect(e.target.value)}
            >
              <option value="">Select a Meeting</option>
              {meetings
                .filter((m) =>
                  m.subject.toLowerCase().includes(searchTerm.toLowerCase())
                )
                .map((meeting) => (
                  <option key={meeting.meeting_id} value={meeting.meeting_id}>
                    {meeting.subject}
                  </option>
                ))}
            </select>
            <ChevronDown className="absolute right-3 top-3 text-gray-500 w-5 h-5 pointer-events-none" />
          </div>
        </div>

        {/* Right: Buttons */}
        <div className="flex gap-4">
          {/* Send MOM Button */}
          <button
            onClick={handleSave}
            className="px-5 py-2 flex items-center gap-2 rounded-lg text-white font-semibold bg-blue-600 hover:bg-blue-700 shadow-md"
          >
            <Send className="w-5 h-5" />
            Send MOM
          </button>

          {/* Create Follow-up Meeting Button */}
          <button
            onClick={() => setShowModal(true)}
            className="px-5 py-2 flex items-center gap-2 rounded-lg text-white font-semibold bg-green-600 hover:bg-green-700 shadow-md"
          >
            <CalendarPlus className="w-5 h-5" />
            Create Follow-up Meeting
          </button>
        </div>
      </div>

      {/* MOM Editor Section */}
      <div className="bg-white shadow-md p-4 rounded-lg border relative">
        {/* MOM Editor */}
        {selectedMeeting ? (
          <MomEditor momText={momText} setMomText={setMomText} />
        ) : (
          <p className="text-gray-500 text-center py-4">
            Select a meeting to view MOM
          </p>
        )}

        {/* Generate AI Summary Button (Bottom Right Inside Editor) */}
        <button
          onClick={handleGenerateSummary}
          className={`absolute bottom-4 right-4 px-4 py-2 flex items-center gap-2 rounded-lg text-white font-semibold shadow-md transition ${
            selectedMeeting
              ? "bg-purple-600 hover:bg-purple-700"
              : "bg-gray-400 cursor-not-allowed"
          }`}
          disabled={!selectedMeeting || loadingSummary}
        >
          <Sparkles className="w-5 h-5" />
          {loadingSummary ? "Generating..." : "Generate AI Summary"}
        </button>
      </div>

      {/* AI Summary Section */}
      {aiSummary && (
        <div className="bg-gray-100 p-4 rounded-lg border shadow-md">
          <h2 className="text-lg font-semibold text-gray-700 mb-3">
            AI-Generated Summary
          </h2>

          {/* Discussion Highlights */}
          <div className="mb-3">
            <h3 className="font-semibold text-gray-800">
              Discussion Highlights
            </h3>
            <p className="text-gray-700">{aiSummary.discussion_highlights}</p>
          </div>

          {/* Key Takeaways */}
          <div className="mb-3">
            <h3 className="font-semibold text-gray-800">Key Takeaways</h3>
            <ul className="list-disc list-inside text-gray-700">
              {aiSummary.key_takeaways.map((takeaway, index) => (
                <li key={index}>{takeaway}</li>
              ))}
            </ul>
          </div>

          {/* Action Items */}
          <div className="mb-3">
            <h3 className="font-semibold text-gray-800">Action Items</h3>
            <table className="w-full border-collapse border border-gray-300">
              <thead>
                <tr className="bg-gray-200">
                  <th className="border border-gray-300 px-3 py-2 text-left">
                    Item
                  </th>
                  <th className="border border-gray-300 px-3 py-2 text-left">
                    Deadline
                  </th>
                  <th className="border border-gray-300 px-3 py-2 text-left">
                    Owner
                  </th>
                </tr>
              </thead>
              <tbody>
                {aiSummary.action_items.map((item, index) => (
                  <tr key={index} className="bg-white">
                    <td className="border border-gray-300 px-3 py-2">
                      {item.item}
                    </td>
                    <td className="border border-gray-300 px-3 py-2">
                      {item.deadline}
                    </td>
                    <td className="border border-gray-300 px-3 py-2">
                      {item.owner}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* FAQs Answered */}
          <div className="mb-3">
            <h3 className="font-semibold text-gray-800">FAQs Answered</h3>
            <ul className="list-disc list-inside text-gray-700">
              {aiSummary.faqs_answered.map((faq, index) => (
                <li key={index}>{faq}</li>
              ))}
            </ul>
          </div>

          {/* Next Steps & Risks */}
          <div>
            <h3 className="font-semibold text-gray-800">Next Steps & Risks</h3>
            <p className="text-gray-700">{aiSummary.next_steps_risks}</p>
          </div>
        </div>
      )}
      <FollowUpMeetingModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        mom_data={selectedMeeting.mom_data} // MOM data for API
        attendees={selectedMeeting.attendees} // Attendees for follow-up meeting
        onCreateMeeting={async (meetingData) => {
          const response = await scheduleMeeting(meetingData);
          if (response) {
            console.log("Meeting Scheduled:", response);
            setShowModal(false); // Close modal after success
          }
        }}
        baseUrl={JIRA_API}
      />
    </div>
  );
}
