// Message card functional component with collapsible content
import { useState } from "react";
const MessageCard = ({ title, content, defaultOpen = false }) => {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="mt-3 rounded-lg border-l-4 border-violet-400 bg-violet-50 shadow-sm">
      <button
        type="button"
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-4 py-3"
      >
        <span className="font-medium text-gray-800">{title}</span>
        <span
          className={`transition-transform ${open ? "rotate-90" : ""}`}
          aria-hidden
        >
          ›
        </span>
      </button>

      <div className={open ? "block" : "hidden"}>
        <pre className="px-4 pb-4 whitespace-pre-wrap break-words overflow-x-auto text-gray-700">
          {content}
        </pre>
      </div>
    </div>
  );
};

export default MessageCard;
