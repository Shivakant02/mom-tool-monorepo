import mongoose from "mongoose";

const actionItemSchema = new mongoose.Schema({
  item: { type: String, required: false }, // Allow missing values
  deadline: { type: String, required: false }, // Allow missing values
  owner: { type: String, required: false }, // Allow missing values
  email: { type: String, required: false }, // Allow missing values
});

const momSchema = new mongoose.Schema({
  meeting_id: { type: String, required: true, unique: true },
  event_id: { type: String, required: false, unique: true },
  subject: { type: String, required: true },
  mom_data: {
    organizer: { type: String, required: true },
    discussion_topics: [{ type: String }],
    key_points: [{ type: String }],
    faqs: [{ type: String }],
    action_items: [actionItemSchema], // Array of action items
  },
  attendees: [{ type: String }],
});

const MoM = mongoose.model("MoM", momSchema);

export default MoM;
