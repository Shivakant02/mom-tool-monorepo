import { useState, useEffect } from "react";
import { CalendarDays } from "lucide-react";
import { upcomingEvents } from "../services/Meeting-service";
import MeetingCard from "../components/cards/MeetingCard";

const MeetingsPage = () => {
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadMeetings = async () => {
      try {
        const meetingsData = await upcomingEvents();
        setMeetings(meetingsData);
      } catch (err) {
        setError("Failed to load meetings.");
      } finally {
        setLoading(false);
      }
    };

    loadMeetings();
  }, []);

  return (
    <div className="container mx-auto p-6">
      <div className="flex items-center gap-3 mb-6">
        <CalendarDays className="w-8 h-8 text-primary" />
        <h1 className="text-2xl font-bold">Upcoming Meetings</h1>
      </div>

      {loading ? (
        <p className="text-gray-500">Loading meetings...</p>
      ) : error ? (
        <p className="text-red-500">{error}</p>
      ) : meetings.length === 0 ? (
        <p className="text-gray-500">No meetings scheduled.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {meetings.map((meeting, index) => (
            <MeetingCard key={index} meeting={meeting} />
          ))}
        </div>
      )}
    </div>
  );
};

export default MeetingsPage;
