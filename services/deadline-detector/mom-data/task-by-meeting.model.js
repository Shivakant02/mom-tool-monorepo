import mongoose from "mongoose";

const MeetingSchema = new mongoose.Schema({
  meetingId: { type: String, required: true, unique: true },
  subject: { type: String, required: true },
  tasks: { type: [String], default: [] }, // Array of Jira task IDs
  createdAt: { type: Date, default: Date.now },
});

const Meeting = mongoose.model("Meeting", MeetingSchema);

export default Meeting;
