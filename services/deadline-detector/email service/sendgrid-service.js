import sgMail from "@sendgrid/mail";
import dotenv from "dotenv";
dotenv.config();
sgMail.setApiKey(process.env.SENDGRID_KEY); // put in .env file

export const sendDeadlineEmail = async ({
  to,
  taskId,
  missingFields,
  cc = [],
}) => {
  const missingFieldsFormatted = missingFields
    .map((field) => `<li>${field}</li>`)
    .join("");

  const taskLink = `${process.env.JIRA_BASE_URL}/jira/software/projects/${process.env.JIRA_PROJECT_KEY}/list?selectedIssue=${taskId}`;

  const msg = {
    to,
    from: process.env.SENDGRID_FROM_EMAIL,
    subject: `🚨 Task ID ${taskId}: Missing Fields Alert`,
    cc: cc.length > 0 ? cc : undefined,
    text: `Task ID: ${taskId} is missing the following fields: ${missingFields.join(
      ", "
    )}. Please update them ASAP.\nView Task: ${taskLink}`,
    html: `
      <h2>🚨 Missing Fields Alert for Task ID: ${taskId}</h2>
      <p><strong>Missing Fields:</strong></p>
      <ul>${missingFieldsFormatted}</ul>
      <p>Please update the missing fields as soon as possible in the system.</p>
      <p>🔗 <a href="${taskLink}" target="_blank">Click here to view the Task in Jira</a></p>
      <br>
      <p>Regards,<br>Automation Bot</p>
    `,
  };

  try {
    await sgMail.send(msg);
    console.log(
      `✅ Email sent to ${to} ${
        cc.length > 0 ? `and cc to ${cc.join(", ")}` : ""
      }`
    );
  } catch (error) {
    console.error("❌ SendGrid Error:", error.response?.body || error.message);
    throw error;
  }
};

export const notifyAssigneeMissingFields = async ({
  to,
  taskId,
  missingFields,
}) => {
  const missingFieldsFormatted = missingFields
    .map((field) => `<li>${field}</li>`)
    .join("");

  const msg = {
    to,
    from: process.env.SENDGRID_FROM_EMAIL,
    subject: `⚠️ Task Assignment Notice - Task ID ${taskId} Missing Fields`,
    text: `You have been assigned Task ID ${taskId}, but it is missing the following fields: ${missingFields.join(
      ", "
    )}. Please review the task.`,
    html: `
      <h2>⚠️ Task Assignment Alert</h2>
      <p>Hello,</p>
      <p>You have been assigned <strong>Task ID: ${taskId}</strong>, but the following fields are missing:</p>
      <ul>${missingFieldsFormatted}</ul>
      <p>Please coordinate with your project manager or update the details as soon as possible.</p>
      <br>
      <p>Regards,<br>Automation Bot 🤖</p>
    `,
  };

  try {
    await sgMail.send(msg);
    console.log(`✅ Notification email sent to ${to}`);
  } catch (error) {
    console.error("❌ SendGrid Error:", error.response?.body || error.message);
    throw error;
  }
};
