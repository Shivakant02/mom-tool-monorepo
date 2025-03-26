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

// // 3️⃣ Update Due Date (PUT)
// export const updateDueDate = async (issueKey, dueDate) => {
//   try {
//     const updateData = { fields: { duedate: dueDate } };

//     const response = await axios.put(
//       `${JIRA_BASE_URL}/rest/api/3/issue/${issueKey}`,
//       updateData,
//       {
//         headers: {
//           Authorization: getAuthHeader(),
//           Accept: "application/json",
//           "Content-Type": "application/json",
//         },
//       }
//     );

//     if (response.status === 204) {
//       console.log(`✅ Due Date Updated for ${issueKey}`);
//     } else {
//       throw new Error(`Failed to update due date for ${issueKey}`);
//     }
//   } catch (error) {
//     console.error(
//       `❌ Error updating due date for ${issueKey}:`,
//       error.response?.data || error.message
//     );
//   }
// };
