// Message card functional component with collapsible content
import { useState } from 'react';
const StepCard = ({ title, content, imageData, defaultOpen = false }) => {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="mt-3 rounded-lg border border-[hsl(var(--accent))]/30 bg-[hsl(var(--background))]/50 shadow-sm transition-shadow hover:border-[hsl(var(--accent))]/70 hover:shadow-md">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex w-full cursor-pointer items-center justify-between px-4 py-3"
      >
        <span className="font-medium">{title}</span>
        <span className={`transition-transform ${open ? 'rotate-90' : ''}`} aria-hidden>
          ›
        </span>
      </button>

      <div className={open ? 'block' : 'hidden'}>
        {imageData ? (
          <div className="px-4 pb-4">
            <img
              src={`data:image/png;base64,${imageData.data}`}
              alt="Sales Graph"
              className="w-full rounded-lg"
            />
          </div>
        ) : (
          <pre className="px-4 pt-3 pb-4 text-xs leading-relaxed text-[hsl(var(--foreground))]/80">
            {content}
          </pre>
        )}
      </div>
    </div>
  );
};

export default StepCard;
