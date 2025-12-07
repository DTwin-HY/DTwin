import { useEffect, useRef, useState } from 'react';
import { ArrowDown } from 'lucide-react';
import MessageCard from './MessageCard';

const ListMessages = ({ messages }) => {
  const bottomRef = useRef(null);
  const [showScrollButton, setShowScrollButton] = useState(false);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    const handleScroll = () => {
      const scrolledUp =
        window.scrollY + window.innerHeight < document.body.scrollHeight - 100;
      setShowScrollButton(scrolledUp);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  if (!Array.isArray(messages) || messages.length === 0) return null;

  return (
    <div className="relative">
      {messages
        .slice()
        .reverse()
        .map((message, idx) => {
          const role = String(message.role ?? message.user ?? '').toLowerCase();

          if (role === 'supervisor') {
            const finalResponse = message.finalMessage;
            const steps = message.steps ?? [];
            return (
              <MessageCard
                key={`msg-${idx}`}
                finalMessage={finalResponse}
                steps={steps}
              />
            );
          }

          if (role === 'user') {
            const userMessage = message.message;
            return (
              <div
                key={`msg-${idx}`}
                className="mt-6 rounded-2xl border border-sky-300 bg-sky-50/30 p-5 shadow-sm backdrop-blur-sm"
              >
                <p className="mb-1 font-semibold text-sky-600">You:</p>
                <p className="whitespace-pre-wrap text-slate-800">{userMessage}</p>
              </div>
            );
          }

          return null;
        })}

      <div ref={bottomRef} />

      {showScrollButton && (
        <button
          onClick={() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' })}
          className="fixed bottom-4 right-10 h-10 w-10 rounded-full bg-purple-600 text-white shadow-lg hover:bg-purple-700 flex items-center justify-center transition-opacity duration-300"
        >
          <ArrowDown size={26} strokeWidth={2.3} />
        </button>
      )}
    </div>
  );
};

export default ListMessages;
