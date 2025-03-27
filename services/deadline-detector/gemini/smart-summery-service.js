import { GoogleGenerativeAI } from "@google/generative-ai";
import "dotenv/config";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

export async function getSmartSummary(inputData) {
  try {
    const model = genAI.getGenerativeModel({
      model: "gemini-1.5-pro",
    });

    // Strict JSON output enforcement
    const prompt = `
  You are an expert meeting summarizer. Given the following Meeting Minutes (MOM) data, generate a well-structured JSON summary with the following sections:

  - **discussion_highlights**: Summarize the main topics discussed concisely.
  - **key_takeaways**: List critical insights from the discussion in bullet points.
  - **action_items** (array): A list of key actions, each with:
    - **item**: The task description (make it actionable and specific).
    - **deadline**: Clear due date (if available) or "TBD" if unknown.
    - **owner**: The responsible person or team.
  - **faqs_answered**: List any frequently asked questions addressed in the meeting.
  - **next_steps_risks**: Clearly outline what happens next and potential challenges.

  --- MOM Data ---
  ${JSON.stringify(inputData)}

  **Ensure the output is**:
  - **Concise** but **informative**.
  - In **valid JSON format** (no extra text, no explanations).
  - Focused on **clarity, accuracy, and actionability**.
`;

    console.log("Sending Prompt:", prompt);

    // Generate response using proper structure
    const result = await model.generateContent({
      contents: [{ role: "user", parts: [{ text: prompt }] }],
      generationConfig: {
        temperature: 0.3, // Lower randomness for structured responses
        responseMimeType: "application/json", // Ensures JSON format
      },
    });

    // console.log("Raw API Response:", JSON.stringify(result, null, 2));

    if (
      !result?.response?.candidates ||
      result.response.candidates.length === 0
    ) {
      throw new Error("No valid candidates returned from Gemini API.");
    }

    // Extract response text
    let responseText =
      result.response.candidates[0]?.content?.parts?.[0]?.text || "";

    // console.log("Raw response text from Gemini:", responseText);

    // Attempt to parse JSON directly
    try {
      const parsedJSON = JSON.parse(responseText);
      console.log("Extracted JSON:", parsedJSON);
      return parsedJSON;
    } catch (parseError) {
      console.error("Invalid JSON from Gemini:", responseText);
      throw new Error("Gemini returned an invalid JSON format.");
    }
  } catch (error) {
    console.error("Error generating summary:", error.message);
    throw new Error("Failed to generate summary.");
  }
}

export async function generateFollowUpAgenda(momData) {
  try {
    const model = genAI.getGenerativeModel({
      model: "gemini-1.5-pro",
    });

    const prompt = `
      You are an expert meeting planner. Based on the last Meeting Minutes (MOM), generate a **Follow-Up Meeting Agenda**.
      
      The agenda must include:
      - **Review of Previous Topics**: Briefly summarize past discussion topics.
      - **Status of Action Items**: Update on pending action items (highlight overdue ones).
      - **Outstanding Issues & Risks**: Any unresolved issues from the last meeting.
      - **Pending FAQs**: Address any unanswered or follow-up questions.
      - **New Topics for Discussion**: Suggest topics that should be discussed in the next meeting.

      MOM Data:
      ${JSON.stringify(momData)}

      Ensure the output is **valid JSON** with this structure, embedding a well-formatted HTML version of the agenda:

      \`\`\`json
      {
        "meeting_agenda": {
          "review_previous_topics": [...],
          "status_action_items": [...],
          "outstanding_issues": [...],
          "pending_faqs": [...],
          "new_discussion_topics": [...]
        },
        "html_agenda": "<html>...</html>"
      }
      \`\`\`

      The **html_agenda** must be a valid HTML string with proper formatting:
      - Use **h2** for the main heading and **h3** for sections.
      - Use **ul & li** for lists.
      - Include a clean **CSS styling** inside a **<style>** block.
      - Ensure it's **directly usable in an email**.

      Do **not** include explanations, just return the JSON output.
    `;

    // console.log("Sending Prompt:", prompt);

    const result = await model.generateContent({
      contents: [{ role: "user", parts: [{ text: prompt }] }],
      generationConfig: {
        temperature: 0.3,
        responseMimeType: "application/json",
      },
    });

    // console.log("Raw API Response:", JSON.stringify(result, null, 2));

    if (
      !result?.response?.candidates ||
      result.response.candidates.length === 0
    ) {
      throw new Error("No valid candidates returned from Gemini API.");
    }

    let responseText =
      result.response.candidates[0]?.content?.parts?.[0]?.text || "";

    // console.log("Raw response text from Gemini:", responseText);

    try {
      const parsedResponse = JSON.parse(responseText);
      console.log("Extracted JSON with HTML:", parsedResponse);

      return parsedResponse;
    } catch (parseError) {
      console.error("Invalid JSON from Gemini:", responseText);
      throw new Error("Gemini returned an invalid JSON format.");
    }
  } catch (error) {
    console.error("Error generating agenda:", error.message);
    throw new Error("Failed to generate agenda.");
  }
}
