// src/components/mom/MomEditor.jsx
export default function MomEditor({ momText, setMomText }) {
  return (
    <textarea
      className="textarea textarea-bordered w-full min-h-[400px] p-4 font-mono bg-base-200 rounded-xl"
      value={JSON.stringify(JSON.parse(momText), null, 2)} // auto-format JSON on each render
      onChange={(e) => setMomText(e.target.value)}
    />
  );
}
