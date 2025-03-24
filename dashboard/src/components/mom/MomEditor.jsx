// src/components/mom/MomEditor.jsx
export default function MomEditor({ momText, setMomText }) {
  return (
    <textarea
      className="textarea textarea-bordered w-full min-h-[400px] p-4 font-mono bg-base-200 rounded-xl"
      value={momText} // just treat it as plain text now
      onChange={(e) => setMomText(e.target.value)}
    />
  );
}
