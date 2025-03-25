// src/pages/MomPage.jsx
import { useState } from "react";
import MomEditor from "../components/mom/MomEditor";
import MomActions from "../components/mom/MomActions";
import jsonData from "../components/mom/mom.json";
import { formatMomJson, parseMomText } from "./formatMomJson";

export default function MomPage() {
  const [momText, setMomText] = useState(formatMomJson(jsonData));
  const textFile = `
  Organizer: Sarah Chen

Discussion Topics:
  1. Sprint planning for 2.5 release
  2. Authentication system update
  3. New dashboard feature progress
  4. Testing strategy for the release
  5. Documentation updates

Key Points:
  - Marcus resolved the caching issue with a 40% improvement in response time.
  - David is working on the OAuth 2.0 integration but needs three more days for the token refresh mechanism.
  - Team members agreed to split the work on the new dashboard feature.
  - Priya aims to increase unit test coverage to above 85% before the release.
  - Documentation updates are needed for the new features, with specific assignments.

FAQs:
  Q1: What is the status of the OAuth token refresh mechanism?
  Q2: How are we dividing the work for the dashboard feature?
  Q3: What is our testing strategy for the new features?
  Q4: When are the documentation updates due?

Action Items:
  1. Review caching code changes
     Deadline: Tomorrow afternoon
     Owner: Priya Patel
  2. Complete OAuth token refresh mechanism
     Deadline: Next Tuesday afternoon
     Owner: K Pavan
     Email: k.pavan@lumiq.ai
  3. Pair with David to resolve OAuth issues
     Deadline: Today at 2 PM
     Owner: Lokesh Kumawat
     Email: lokesh.kumawat@lumiq.ai
  4. Improve user error messages
     Deadline: End of next week
     Owner: Shivakant
     Email: shivakant1@lumiq.ai
  5. Complete metrics chart for dashboard
     Deadline: Next Friday
     Owner: David Kim
  6. Complete user activity timeline for dashboard
     Deadline: Next Friday
     Owner: Priya Patel
  7. Complete status overview widget for dashboard
     Deadline: Next Friday
     Owner: Sarah Chen
  8. Complete resource allocation chart and alerts panel for dashboard
     Deadline: Next Friday
     Owner: Marcus Johnson
  9. Set up end-to-end testing framework
     Deadline: Next Thursday
     Owner: David Kim
  10. Reach 85% test coverage
     Deadline: End of the month
     Owner: Priya Patel
  11. Complete dashboard integration tests
     Deadline: End of the month
     Owner: Marcus Johnson
  12. Update API documentation
     Deadline: April 2nd
     Owner: Priya Patel
  13. Handle developer documentation for authentication system
     Deadline: End of the month
     Owner: David Kim
  14. Write technical details for dashboard framework documentation
     Deadline: End of the month
     Owner: Marcus Johnson
  `;
  const res = parseMomText(textFile);
  console.log(res);

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold mb-4">Meeting Minutes (MOM)</h1>
      <MomEditor momText={momText} setMomText={setMomText} />
      <MomActions momText={momText} />
    </div>
  );
}
