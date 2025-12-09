import { useState } from 'react';
import StepCard from './StepCard';

const MessageCard = ({ finalMessage, steps, defaultOpen = false }) => {
  const [open, setOpen] = useState(defaultOpen);

  // Jos käyttäjä valitsee tekstiä, älä avaa korttia.
  const handleClick = () => {
    const sel = window.getSelection?.();
    if (sel && sel.toString().length > 0) return;
    setOpen((o) => !o);
  };

  return (
    <div className="mt-6 mb-6 rounded-2xl border border-[#b788d8] bg-[#f9f5fa] p-5 shadow-lg transition-all">
      <button
        type="button"
        onClick={handleClick}
        className="group flex w-full cursor-pointer items-start justify-between px-0 py-3 text-left"
      >
        <div>
          <p className="mb-1 font-semibold text-[#9639ad]">DTwin Assistant:</p>
          <p className="cursor-text whitespace-pre-wrap text-slate-800 select-text">
            {finalMessage}
          </p>
        </div>
        <span
          className={`mt-1 text-slate-700 transition-transform ${open ? 'rotate-90' : ''}`}
          aria-hidden
        >
          ›
        </span>
      </button>

      <div className={open ? 'block' : 'hidden'}>
        {steps.map((msg, i) => (
          <StepCard
            key={i}
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

export default MessageCard;
