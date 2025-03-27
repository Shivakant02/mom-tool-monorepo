import { useState, useEffect } from "react";
import { History } from "lucide-react";
import { pastEvents } from "../services/Meeting-service";
import MeetingCard from "../components/cards/MeetingCard";

const PastMeeting = () => {
  const [pastMeetings, setPastMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadMeetings = async () => {
      try {
        const meetingsData = await pastEvents();
        setPastMeetings(meetingsData);
      } catch (err) {
        setError("Failed to load past meetings.");
      } finally {
        setLoading(false);
      }
    };

    loadMeetings();
  }, []);

  return (
    <div className="container mx-auto p-6">
      <div className="flex items-center gap-3 mb-6">
        <History className="w-8 h-8 text-primary" />
        <h1 className="text-2xl font-bold">Past Meetings</h1>
      </div>

      {loading ? (
        <p className="text-gray-500">Loading past meetings...</p>
      ) : error ? (
        <p className="text-red-500">{error}</p>
      ) : pastMeetings.length === 0 ? (
        <p className="text-gray-500">No past meetings found.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {pastMeetings.map((meeting, index) => (
            <MeetingCard key={index} meeting={meeting} disableJoin={true} />
          ))}
        </div>
      )}
    </div>
  );
};

export default PastMeeting;
