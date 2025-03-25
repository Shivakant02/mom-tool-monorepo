export function formatMomJson(json) {
  // If json contains a nested "mom_data", use it
  const actualMom = json.mom_data ? json.mom_data : json;

  let result = `Organizer: ${actualMom.organizer || ""}\n\n`;

  result += "Discussion Topics:\n";
  (actualMom.discussion_topics || []).forEach((topic, idx) => {
    result += `  ${idx + 1}. ${topic}\n`;
  });

  result += "\nKey Points:\n";
  (actualMom.key_points || []).forEach((point, idx) => {
    result += `  - ${point}\n`;
  });

  result += "\nFAQs:\n";
  (actualMom.faqs || []).forEach((faq, idx) => {
    result += `  Q${idx + 1}: ${faq}\n`;
  });

  result += "\nAction Items:\n";
  (actualMom.action_items || []).forEach((item, idx) => {
    result += `  ${idx + 1}. ${item.item || ""}\n     Deadline: ${
      item.deadline || ""
    }\n     Owner: ${item.owner || ""}\n`;
    if (item.email) {
      result += `     Email: ${item.email}\n`;
    }
  });

  return result;
}

export function parseMomText(text) {
  const lines = text.split("\n").map((line) => line.trim());
  let jsonData = { mom_data: {} };

  let currentSection = null;
  let actionItems = [];
  let currentAction = null;

  lines.forEach((line) => {
    if (line.startsWith("Organizer:")) {
      jsonData.mom_data.organizer = line.replace("Organizer: ", "").trim();
    } else if (line.startsWith("Discussion Topics:")) {
      currentSection = "discussion_topics";
      jsonData.mom_data[currentSection] = [];
    } else if (line.startsWith("Key Points:")) {
      currentSection = "key_points";
      jsonData.mom_data[currentSection] = [];
    } else if (line.startsWith("FAQs:")) {
      currentSection = "faqs";
      jsonData.mom_data[currentSection] = [];
    } else if (line.startsWith("Action Items:")) {
      currentSection = "action_items";
      jsonData.mom_data[currentSection] = [];
    } else if (currentSection === "discussion_topics" && line.match(/^\d+\./)) {
      jsonData.mom_data[currentSection].push(line.replace(/^\d+\.\s*/, ""));
    } else if (currentSection === "key_points" && line.startsWith("-")) {
      jsonData.mom_data[currentSection].push(line.replace("- ", ""));
    } else if (currentSection === "faqs" && line.match(/^Q\d+:/)) {
      jsonData.mom_data[currentSection].push(line.replace(/^Q\d+:\s*/, ""));
    } else if (currentSection === "action_items") {
      if (line.match(/^\d+\./)) {
        if (currentAction) {
          actionItems.push(currentAction);
        }
        currentAction = { item: line.replace(/^\d+\.\s*/, "") };
      } else if (line.startsWith("Deadline:")) {
        currentAction.deadline = line.replace("Deadline: ", "").trim();
      } else if (line.startsWith("Owner:")) {
        currentAction.owner = line.replace("Owner: ", "").trim();
      } else if (line.startsWith("Email:")) {
        currentAction.email = line.replace("Email: ", "").trim();
      }
    }
  });

  if (currentAction) {
    actionItems.push(currentAction);
  }
  jsonData.mom_data.action_items = actionItems;

  return jsonData;
}
