import { useState } from "react";
import MessageCard from "./MessageCard"; // oletetaan että sama MessageCard on olemassa

const FinalMessageCard = ({ body, messages, defaultOpen = false }) => {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="mt-6 rounded-lg border-l-4 border-violet-400 bg-violet-50 p-4">
      {/* Ryhmän otsikko */}
        <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-start justify-between px-0 py-3 text-left"
        >
        <div>
          <p className="text-black-800 mb-1">Supervisor:</p>
          <p className="whitespace-pre-wrap text-gray-700">{body}</p>
        </div>
        <span className={`transition-transform mt-1 ${open ? "rotate-90" : ""}`} aria-hidden>
            ›
        </span>
        </button>
      {/* Sisältö: lista MessageCardeista */}
      <div className={open ? "block" : "hidden"}>
        {messages.map((msg, index) => (
          <MessageCard
            key={index}
            title={msg.title}
            content={msg.body}
            imageData={msg.imageData}
            defaultOpen={msg.defaultOpen || false}
          />
        ))}
      </div>
    </div>
  );
};

export default FinalMessageCard;
