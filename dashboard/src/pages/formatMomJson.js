export function formatMomJson(json) {
  const mom = json.mom_data;

  let result = `Organizer: ${mom.organizer}\n\n`;

  result += "Discussion Topics:\n";
  mom.discussion_topics.forEach((topic, idx) => {
    result += `  ${idx + 1}. ${topic}\n`;
  });

  result += "\nKey Points:\n";
  mom.key_points.forEach((point, idx) => {
    result += `  - ${point}\n`;
  });

  result += "\nFAQs:\n";
  mom.faqs.forEach((faq, idx) => {
    result += `  Q${idx + 1}: ${faq}\n`;
  });

  result += "\nAction Items:\n";
  mom.action_items.forEach((item, idx) => {
    result += `  ${idx + 1}. ${item.item}\n     Deadline: ${
      item.deadline
    }\n     Owner: ${item.owner}\n`;
    if (item.email) {
      result += `     Email: ${item.email}\n`;
    }
  });

  return result;
}
