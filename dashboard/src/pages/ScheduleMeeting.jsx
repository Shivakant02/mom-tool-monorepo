import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { scheduleMeeting } from "../services/scheduleMeeting";

export default function ScheduleMeetingForm() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    subject: "",
    start: { dateTime: "", timeZone: "Asia/Kolkata" },
    end: { dateTime: "", timeZone: "Asia/Kolkata" },
    attendees: [],
    isOnlineMeeting: true,
    onlineMeetingProvider: "teamsForBusiness",
  });

  const [attendeeEmail, setAttendeeEmail] = useState("");

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleDateChange = (key, value) => {
    setFormData({ ...formData, [key]: { ...formData[key], dateTime: value } });
  };

  const addAttendee = () => {
    if (attendeeEmail) {
      if (formData.attendees.some((a) => a.emailAddress === attendeeEmail)) {
        alert("Attendee already added!");
        return;
      }

      setFormData({
        ...formData,
        attendees: [
          ...formData.attendees,
          { emailAddress: attendeeEmail, type: "required" },
        ],
      });

      setAttendeeEmail("");
    }
  };

  const removeAttendee = (index) => {
    setFormData({
      ...formData,
      attendees: formData.attendees.filter((_, i) => i !== index),
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await scheduleMeeting(formData);
      alert("Meeting Scheduled Successfully!");

      setFormData({
        subject: "",
        start: { dateTime: "", timeZone: "Asia/Kolkata" },
        end: { dateTime: "", timeZone: "Asia/Kolkata" },
        attendees: [],
        isOnlineMeeting: true,
        onlineMeetingProvider: "teamsForBusiness",
      });
    } catch (error) {
      alert(error.message);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-8 border border-gray-300 rounded-lg shadow-lg bg-white">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6 text-center">
        📅 Schedule a Meeting
      </h2>

      <form onSubmit={handleSubmit} className="flex flex-col gap-6">
        <input
          type="text"
          name="subject"
          value={formData.subject}
          onChange={handleInputChange}
          placeholder="Meeting Subject"
          className="input input-bordered w-full"
          required
        />

        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="block text-gray-600 text-sm mb-1">
              Start Time
            </label>
            <input
              type="datetime-local"
              value={formData.start.dateTime}
              onChange={(e) => handleDateChange("start", e.target.value)}
              className="input input-bordered w-full"
              required
            />
          </div>
          <div>
            <label className="block text-gray-600 text-sm mb-1">End Time</label>
            <input
              type="datetime-local"
              value={formData.end.dateTime}
              onChange={(e) => handleDateChange("end", e.target.value)}
              className="input input-bordered w-full"
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-gray-600 text-sm mb-1">
            Add Attendees
          </label>
          <div className="flex items-center gap-4">
            <input
              type="email"
              value={attendeeEmail}
              onChange={(e) => setAttendeeEmail(e.target.value)}
              placeholder="Attendee Email"
              className="input input-bordered flex-grow"
            />
            <button
              type="button"
              onClick={addAttendee}
              className="btn btn-primary px-6 py-2 rounded-lg text-2xl"
            >
              +
            </button>
          </div>
        </div>

        {formData.attendees.length > 0 && (
          <div className="mt-4 space-y-2">
            {formData.attendees.map((attendee, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 bg-gray-100 rounded-md"
              >
                <span className="text-gray-800">{attendee.emailAddress}</span>
                <button
                  type="button"
                  onClick={() => removeAttendee(index)}
                  className="text-red-500 hover:text-red-700"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}

        <button type="submit" className="btn btn-primary w-full py-3 text-lg">
          ✅ Schedule Meeting
        </button>

        {/* Buttons for past and upcoming events */}
        <div className="flex justify-between mt-4">
          <button
            onClick={() => navigate("/upcoming-events")}
            className="btn bg-white border border-gray-400 text-gray-800 w-1/2 mr-2 hover:bg-gray-100"
          >
            📅 View Upcoming Events
          </button>
          <button
            onClick={() => navigate("/past-events")}
            className="btn bg-white border border-gray-400 text-gray-800 w-1/2 ml-2 hover:bg-gray-100"
          >
            📜 View Past Events
          </button>
        </div>
      </form>
    </div>
  );
}
