// Message card functional component with collapsible content
import { useState } from 'react';
const MessageCard = ({ title, content, imageData, defaultOpen = false }) => {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="mt-3 rounded-lg border-l-4 border-violet-400 bg-violet-50 shadow-sm">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center justify-between px-4 py-3"
      >
        <span className="font-medium text-gray-800">{title}</span>
        <span className={`transition-transform ${open ? 'rotate-90' : ''}`} aria-hidden>
          ›
        </span>
      </button>

      <div className={open ? 'block' : 'hidden'}>
        {imageData ? (
          <div className="px-4 pb-4">
            <img
              src={`data:image/${imageData.format};base64,${imageData.data}`}
              alt={imageData.caption || 'Sales graph'}
              className="w-full rounded-lg"
            />
            {imageData.caption && (
              <p className="mt-2 text-center text-sm text-gray-600">{imageData.caption}</p>
            )}
          </div>
        ) : (
          <pre className="overflow-x-auto px-4 pb-4 break-words whitespace-pre-wrap text-gray-700">
            {content}
          </pre>
        )}
      </div>
    </div>
  );
};

export default MessageCard;
