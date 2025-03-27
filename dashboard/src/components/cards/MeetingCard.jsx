import { Calendar, Clock, Users, Video } from "lucide-react";

const MeetingCard = ({ meeting, disable = false }) => {
  if (!meeting) return null; // Prevents errors if meeting is undefined

  const { subject, startTime, endTime, organizer, attendees, joinUrl } =
    meeting;

  // Check if the event has already ended
  const isPastEvent = new Date(endTime) < new Date();

  return (
    <div className="bg-white shadow-lg border border-gray-300 rounded-lg p-4 w-full max-w-md flex flex-col">
      {/* Subject */}
      <h2 className="text-lg font-semibold flex items-center gap-2 text-gray-800 pb-3 border-b">
        <Calendar className="w-5 h-5 text-primary" /> {subject}
      </h2>

      {/* Time */}
      <div className="py-3 border-b flex items-center gap-2 text-gray-600 text-sm">
        <Clock className="w-4 h-4 text-secondary" />
        {new Date(startTime).toLocaleString()} -{" "}
        {new Date(endTime).toLocaleString()}
      </div>

      {/* Organizer */}
      <div className="py-3 border-b flex items-center gap-2 text-gray-600 text-sm">
        <Users className="w-4 h-4 text-accent" />
        <span>Organizer: {organizer}</span>
      </div>

      {/* Attendees */}
      <div className="py-3 border-b flex-grow">
        <p className="text-gray-600 text-sm mb-1">Attendees:</p>
        <div className="max-h-16 overflow-y-auto text-sm text-gray-700 border border-gray-300 p-2 rounded">
          {attendees.length > 0 ? attendees.join(", ") : "None"}
        </div>
      </div>

      {/* Join Button (Fixed at Bottom) */}
      <div className="mt-auto">
        <button
          className={`btn btn-primary font-black w-full flex items-center gap-2 justify-center transition-all ${
            isPastEvent || disable
              ? "opacity-100 cursor-not-allowed"
              : "hover:scale-105"
          }`}
          disabled={isPastEvent || disable}
          onClick={() =>
            !isPastEvent && !disable && window.open(joinUrl, "_blank")
          }
        >
          <Video className="w-4 h-4" />{" "}
          {isPastEvent ? "Meeting Ended" : "Join Meeting"}
        </button>
      </div>
    </div>
  );
};

export default MeetingCard;
