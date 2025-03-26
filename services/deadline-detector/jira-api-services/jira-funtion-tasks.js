import axios from "axios";

// Config
const JIRA_BASE_URL = process.env.JIRA_BASE_URL;

// Auth Header Generator
const getAuthHeader = () => {
  const { JIRA_EMAIL, JIRA_API_TOKEN } = process.env;
  return `Basic ${Buffer.from(`${JIRA_EMAIL}:${JIRA_API_TOKEN}`).toString(
    "base64"
  )}`;
};

// 1️⃣ Get Account ID by Email
export const getAccountIdByEmail = async (email) => {
  try {
    const response = await axios.get(
      `${JIRA_BASE_URL}/rest/api/3/user/search?query=${email}`,
      {
        headers: {
          Authorization: getAuthHeader(),
          Accept: "application/json",
        },
      }
    );

    if (response.status === 200 && response.data.length > 0) {
      return response.data[0].accountId;
    } else {
      console.warn(`⚠️ No account ID found for email: ${email}`);
      return null;
    }
  } catch (error) {
    console.error(
      `❌ Error fetching account ID for ${email}:`,
      error.response?.data || error.message
    );
    return null;
  }
};

// 2️⃣ Create Jira Issue
export const createJiraIssue = async (payload) => {
  try {
    const response = await axios.post(
      `${JIRA_BASE_URL}/rest/api/3/issue`,
      payload,
      {
        headers: {
          Authorization: getAuthHeader(),
          Accept: "application/json",
          "Content-Type": "application/json",
        },
      }
    );

    if (response.status === 201) {
      console.log(`✅ Jira Issue Created: ${response.data.key}`);
      return response.data; // { key, id, self, etc. }
    } else {
      console.error(
        "❌ Jira issue creation returned unexpected status:",
        response.status
      );
      return null;
    }
  } catch (error) {
    console.error(
      "❌ Error creating Jira issue:",
      error.response?.data || error.message
    );
    return null;
  }
};

// 3️⃣ Update Missing Fields in Jira Issue
export const updateJiraIssue = async (issueKey, fieldsToUpdate) => {
  try {
    if (!issueKey || Object.keys(fieldsToUpdate).length === 0) {
      return { success: false, message: "No fields to update." };
    }

    if (fieldsToUpdate.assignee) {
      const accountId = await getAccountIdByEmail(fieldsToUpdate.assignee);
      if (accountId) {
        fieldsToUpdate.assignee = { accountId };
      }
    }

    if (fieldsToUpdate.description) {
      fieldsToUpdate.description = {
        type: "doc",
        version: 1,
        content: [
          {
            type: "paragraph",
            content: [{ type: "text", text: fieldsToUpdate.description }],
          },
        ],
      };
    }

    const response = await axios.put(
      `${JIRA_BASE_URL}/rest/api/3/issue/${issueKey}`,
      { fields: fieldsToUpdate },
      {
        headers: {
          Authorization: getAuthHeader(),
          Accept: "application/json",
          "Content-Type": "application/json",
        },
      }
    );

    if (response.status === 204) {
      // Jira returns 204 No Content on a successful update
      console.log(`✅ Jira Issue Updated: ${issueKey}`);
      return {
        success: true,
        message: "Jira task updated successfully!",
        updatedFields: fieldsToUpdate,
      };
    } else {
      console.warn(`⚠️ Unexpected response status: ${response.status}`);
      return {
        success: false,
        message: `Unexpected response status: ${response.status}`,
      };
    }
  } catch (error) {
    console.error(
      "❌ Error updating Jira issue:",
      error.response?.data || error.message
    );
    return { success: false, error: error.response?.data || error.message };
  }
};
