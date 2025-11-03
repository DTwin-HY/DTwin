import MessageCard from "./MessageCard";

const ListMessages = ({ messages }) => {
  console.log('ListMessages received messages:', messages);
  if (!Array.isArray(messages) || messages.length === 0) return null;

  return (
    <div className="space-y-4">
      {messages.slice().reverse().map((message, idx) => {
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
              className="mt-6 rounded-lg border-l-4 border-teal-400 bg-teal-50 p-4"
            >
              <p className="text-black-800 mb-1">Your message:</p>
              <p className="whitespace-pre-wrap text-gray-700">{userMessage}</p>
            </div>
          );
        }

        return null;
      })}
    </div>
  );
};

export default ListMessages;