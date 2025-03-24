// src/pages/MomPage.jsx
import { useState } from "react";
import MomEditor from "../components/mom/MomEditor";
import MomActions from "../components/mom/MomActions";
import jsonData from "../components/mom/mom.json";
import { formatMomJson } from "./formatMomJson";

export default function MomPage() {
  const [momText, setMomText] = useState(formatMomJson(jsonData));

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold mb-4">Meeting Minutes (MOM)</h1>
      <MomEditor momText={momText} setMomText={setMomText} />
      <MomActions momText={momText} />
    </div>
  );
}
