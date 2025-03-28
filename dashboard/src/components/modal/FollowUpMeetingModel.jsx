import { useState, useEffect } from "react";
import axios from "axios";

export default function FollowUpMeetingModal({
  isOpen,
  onClose,
  attendees,
  mom_data,
  onCreateMeeting,
  baseUrl,
}) {
  const [meetingSubject, setMeetingSubject] = useState("Follow-up Meeting");
  const [rawMeetingAgenda, setRawMeetingAgenda] = useState(""); // Store raw HTML
  const [meetingAgenda, setMeetingAgenda] = useState(""); // Store plain text

  const [meetingDate, setMeetingDate] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");

  // Fetch agenda when modal opens
  useEffect(() => {
    if (isOpen) {
      axios
        .post(`${baseUrl}/api/v1/gemini/generate-agenda`, { mom_data })
        .then((response) => {
          const htmlAgenda = response.data.agenda.html_agenda;
          setRawMeetingAgenda(htmlAgenda); // Store raw HTML

          // Convert HTML to plain text
          const parser = new DOMParser();
          const doc = parser.parseFromString(htmlAgenda, "text/html");
          setMeetingAgenda(doc.body.textContent || "No agenda available");
        })
        .catch(() => {
          setRawMeetingAgenda("No agenda available");
          setMeetingAgenda("No agenda available");
        });
    }
  }, [isOpen, mom_data, baseUrl]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50">
      <div className="bg-white bg-opacity-90 backdrop-blur-md border border-gray-300 rounded-xl shadow-2xl w-[600px] max-w-xl p-6 space-y-4 relative">
        {/* Close Button */}
        <button
          className="absolute top-3 right-3 text-gray-600 hover:text-gray-900"
          onClick={onClose}
        >
          ✕
        </button>

        {/* Title */}
        <h2 className="text-xl font-semibold text-center">
          Schedule Follow-up Meeting
        </h2>

        {/* Meeting Subject */}
        <div>
          <label className="block text-sm font-medium">Meeting Subject</label>
          <input
            type="text"
            value={meetingSubject}
            onChange={(e) => setMeetingSubject(e.target.value)}
            className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Date Input */}
        <div>
          <label className="block text-sm font-medium">Date</label>
          <input
            type="date"
            value={meetingDate}
            onChange={(e) => setMeetingDate(e.target.value)}
            className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Start Time Input */}
        <div>
          <label className="block text-sm font-medium">Start Time</label>
          <input
            type="time"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* End Time Input (User Decides) */}
        <div>
          <label className="block text-sm font-medium">End Time</label>
          <input
            type="time"
            value={endTime}
            onChange={(e) => setEndTime(e.target.value)}
            className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Attendees List */}
        <div>
          <label className="block text-sm font-medium">Attendees</label>
          <ul className="list-disc list-inside text-gray-700 pl-4">
            {attendees.map((attendee, index) => (
              <li key={index}>{attendee}</li>
            ))}
          </ul>
        </div>

        {/* Agenda (Displayed as Plain Text) */}
        <div>
          <label className="block text-sm font-medium">Agenda</label>
          <textarea
            value={meetingAgenda}
            readOnly
            className="w-full border border-gray-300 rounded-lg p-2 h-24 bg-gray-100"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between mt-4">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition"
          >
            Cancel
          </button>
          <button
            onClick={() =>
              onCreateMeeting({
                subject: meetingSubject,
                start: {
                  dateTime: `${meetingDate}T${startTime}:00`,
                  timeZone: "Asia/Kolkata",
                },
                end: {
                  dateTime: `${meetingDate}T${endTime}:00`,
                  timeZone: "Asia/Kolkata",
                },
                attendees: attendees.map((email) => ({
                  emailAddress: { address: email },
                })),
                isOnlineMeeting: true,
                onlineMeetingProvider: "teamsForBusiness",
                body: {
                  contentType: "HTML",
                  content: rawMeetingAgenda, // Keeping raw HTML
                },
              })
            }
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Create Meeting
          </button>
        </div>
      </div>
    </div>
  );
}
