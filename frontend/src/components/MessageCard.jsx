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
    <div 
      className="mt-6 rounded-2xl border p-5 shadow-lg transition-all"
      style={{ 
        borderColor: '#dbb6f3ff', 
        backgroundColor: '#f7ecffff',
        fontSize: 19
      }}
    >
      <button
        type="button"
        onClick={handleClick}
        className="group flex w-full cursor-pointer items-start justify-between px-0 py-3 text-left"
      >
        <div>
          <p className="mb-1 font-bold" style={{ color: '#8b5cf6' }}>DTwin Assistant:</p>
          <p className="cursor-text whitespace-pre-wrap select-text" style={{ color: '#1f2937' }}>{finalMessage}</p>
        </div>
        <span className={`mt-1 transition-transform ${open ? 'rotate-90' : ''}`} style={{ color: '#1f2937' }} aria-hidden>
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
