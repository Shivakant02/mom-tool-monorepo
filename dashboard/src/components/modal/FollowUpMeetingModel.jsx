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
  const [meetingAgenda, setMeetingAgenda] = useState("");
  const [meetingDate, setMeetingDate] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");

  // Fetch agenda when modal opens
  useEffect(() => {
    if (isOpen) {
      axios
        .post(`${baseUrl}/api/v1/gemini/generate-agenda`, { mom_data })
        .then((response) => setMeetingAgenda(response.data.agenda.html_agenda))
        .catch(() => setMeetingAgenda("No agenda available"));
    }
  }, [isOpen, mom_data, baseUrl]);

  // Auto-set end time (30 mins after start time)
  const handleStartTimeChange = (e) => {
    const start = e.target.value;
    setStartTime(start);

    if (start) {
      const [hours, minutes] = start.split(":").map(Number);
      const endHours = hours + Math.floor((minutes + 30) / 60);
      const endMinutes = (minutes + 30) % 60;
      setEndTime(
        `${String(endHours).padStart(2, "0")}:${String(endMinutes).padStart(
          2,
          "0"
        )}`
      );
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
      <div className="bg-white p-6 rounded-lg shadow-lg w-96 space-y-4">
        <h2 className="text-xl font-semibold">Schedule Follow-up Meeting</h2>

        {/* Meeting Subject */}
        <div>
          <label className="block text-sm font-medium">Meeting Subject</label>
          <input
            type="text"
            value={meetingSubject}
            onChange={(e) => setMeetingSubject(e.target.value)}
            className="w-full border rounded-lg p-2"
          />
        </div>

        {/* Date Input */}
        <div>
          <label className="block text-sm font-medium">Date</label>
          <input
            type="date"
            value={meetingDate}
            onChange={(e) => setMeetingDate(e.target.value)}
            className="w-full border rounded-lg p-2"
          />
        </div>

        {/* Start Time Input */}
        <div>
          <label className="block text-sm font-medium">Start Time</label>
          <input
            type="time"
            value={startTime}
            onChange={handleStartTimeChange}
            className="w-full border rounded-lg p-2"
          />
        </div>

        {/* End Time Input (Auto-set) */}
        <div>
          <label className="block text-sm font-medium">End Time</label>
          <input
            type="time"
            value={endTime}
            readOnly
            className="w-full border rounded-lg p-2 bg-gray-100"
          />
        </div>

        {/* Attendees List */}
        <div>
          <label className="block text-sm font-medium">Attendees</label>
          <ul className="list-disc list-inside text-gray-700">
            {attendees.map((attendee, index) => (
              <li key={index}>{attendee}</li>
            ))}
          </ul>
        </div>

        {/* Agenda (Prefilled from API) */}
        <div>
          <label className="block text-sm font-medium">Agenda</label>
          <textarea
            value={meetingAgenda}
            readOnly
            className="w-full border rounded-lg p-2 h-20 bg-gray-100"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-400 text-white rounded-lg"
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
                  content: `${meetingAgenda}`,
                },
              })
            }
            className="px-4 py-2 bg-blue-600 text-white rounded-lg"
          >
            Create Meeting
          </button>
        </div>
      </div>
    </div>
  );
}
