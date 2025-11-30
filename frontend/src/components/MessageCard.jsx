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
    <div className="mt-6 rounded-lg border-l-4 border-violet-400 bg-violet-50 p-4">
      <button
        type="button"
        onClick={handleClick}
        className="group flex w-full cursor-pointer items-start justify-between px-0 py-3 text-left"
      >
        <div>
          <p className="mb-1 text-gray-800 font-semibold">DTwin Assistant:</p>
          <p className="cursor-text whitespace-pre-wrap text-gray-700 select-text text-lg">
            {finalMessage}
          </p>
        </div>
        <span className={`mt-1 transition-transform ${open ? 'rotate-90' : ''}`} aria-hidden>
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
