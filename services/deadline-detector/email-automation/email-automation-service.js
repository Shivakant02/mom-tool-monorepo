import axios from "axios";
import dotenv from "dotenv";
dotenv.config();

const JIRA_WEBHOOK_URL = process.env.WEBHOOK_URL;
const JIRA_WEBHOOK_TOKEN = process.env.WEBHOOK_TOKEN;

// Function to send email reminders
const sendReminderEmails = async (issues) => {
  try {
    // Validate issues array
    if (!issues || !Array.isArray(issues) || issues.length === 0) {
      throw new Error("Invalid issues array");
    }

    // Send POST request to Jira webhook
    const response = await axios.post(
      JIRA_WEBHOOK_URL,
      { issues },
      {
        headers: {
          "Content-Type": "application/json",
          "X-Automation-Webhook-Token": JIRA_WEBHOOK_TOKEN,
        },
      }
    );

    return {
      success: true,
      message: "Reminder emails triggered successfully",
      data: response.data,
    };
  } catch (error) {
    console.error(
      "Error sending reminders:",
      error.response?.data || error.message
    );
    return {
      success: false,
      error: "Failed to send reminders",
      details: error.response?.data || error.message,
    };
  }
};

export default sendReminderEmails;
