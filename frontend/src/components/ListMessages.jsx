import { useEffect, useRef } from 'react';
import MessageCard from './MessageCard';

const ListMessages = ({ messages }) => {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  console.log('ListMessages received messages:', messages);
  if (!Array.isArray(messages) || messages.length === 0) return null;

  return (
    <div className="space-y-4 overflow-y-auto">
      {messages
        .slice()
        .reverse()
        .map((message, idx) => {
          const role = String(message.role ?? message.user ?? '').toLowerCase();

          if (role === 'supervisor') {
            const finalResponse = message.finalMessage;
            const steps = message.steps ?? [];
            return <MessageCard key={`msg-${idx}`} finalMessage={finalResponse} steps={steps} />;
          }

          if (role === 'user') {
            const userMessage = message.message;
            return (
              <div
                key={`msg-${idx}`}
                className="mt-6 rounded-2xl border p-5 shadow-lg"
                style={{ borderColor: '#67e8f9', backgroundColor: 'rgba(103, 232, 249, 0.05)', fontSize: 19}}
              >
                <p className="mb-1 font-semibold" style={{ color: '#0891b2' }}>You:</p>
                <p className="whitespace-pre-wrap" style={{ color: '#1f2937' }}>{userMessage}</p>
              </div>
            );
          }

          return null;
        })}

      <div ref={bottomRef} />
    </div>
  );
};

export default ListMessages;
