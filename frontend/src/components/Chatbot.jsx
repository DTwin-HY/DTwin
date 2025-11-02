import { useState } from 'react';
import { streamMessage, fetchChats } from '../api/chatgpt';
import { useAutoClearMessage } from '../hooks/useAutoClearMessage';
import MessageCard from './MessageCard';
import { headerLine } from '../utils/streamFormat';

const Chatbot = () => {
  const [inputValue, setInputValue] = useState('');
  const [userMessage, setUserMessage] = useState('');
  const [responses, setResponses] = useState([]);
  const [finalMessage, setFinalMessage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  // eslint-disable-next-line no-unused-vars
  const [chats, setChats] = useState([]);

  const showSuccess = useAutoClearMessage(successMessage, setSuccessMessage);
  const showError = useAutoClearMessage(errorMessage, setErrorMessage);

  const finalizeLastResponse = () => {
    setResponses((prev) => {
      if (!prev || prev.length === 0) {
        setFinalMessage(null);
        return prev;
      }
      const last = prev[prev.length - 1];
      setFinalMessage(last);
      return prev.slice(0, -1);
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) {
      setErrorMessage('Input cannot be empty');
      return;
    }

    setLoading(true);
    setSuccessMessage('');
    setErrorMessage('');
    setResponses([]);
    setFinalMessage(null);
    setUserMessage(inputValue);

    try {
      await streamMessage(inputValue, (chunk) => {
        if (Array.isArray(chunk)) {
          const cards = chunk.map((update) => {
            const title = headerLine(update);
            let body = '';
            let imageData = null;

            if (update.messages && update.messages.length) {
              update.messages.forEach((msg) => {
                if (msg.image_data) {
                  imageData = msg.image_data;
                }

                const content = msg.content || '';
                if (content) body += `${content}\n`;
                (msg.tool_calls || []).forEach((t) => (body += `→ ${t.name}()\n`));
              });
            }

            return { title, body: body.trim(), imageData };
          });

          setResponses((prev) => [...prev, ...cards]);
        }
      });
      const latest = await fetchChats();
      setChats(latest);
      setSuccessMessage('Prompt and response saved to database!');
      setInputValue('');
    } catch (err) {
      console.error(err);
      setErrorMessage(`Error in backend/database${err?.message ? `: ${err.message}` : ''}`);
    } finally {
      setLoading(false);
      finalizeLastResponse();
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-start bg-gray-100 p-4 pt-8">
      <div className="mt-4 w-[700px] rounded-xl bg-white p-6 shadow-md">
        <h3 className="mb-4 text-lg font-semibold text-gray-800">Ask the Supervisor</h3>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={loading}
            className="min-h-[100px] rounded-lg border border-gray-300 p-4 text-lg focus:ring-2 focus:ring-purple-500 focus:outline-none"
            placeholder="Type your message..."
          />
          <button
            type="submit"
            disabled={loading}
            className="rounded-lg bg-purple-500 py-3 font-semibold text-white shadow transition-colors duration-200 hover:bg-purple-600 disabled:bg-gray-400"
          >
            {loading ? 'Streaming...' : 'Send Message'}
          </button>
        </form>

        {userMessage && (
          <div className="mt-6 rounded-lg border-l-4 border-teal-400 bg-teal-50 p-4">
            <p className="text-black-800 mb-1">Your message:</p>
            <p className="whitespace-pre-wrap text-gray-700">{userMessage}</p>
          </div>
        )}
        {/* Render message cards for each response */}
        {responses.length > 0 && (
          <div>
            {responses.map((r, i) => (
              <MessageCard key={i} title={r.title} content={r.body} imageData={r.imageData} />
            ))}
          </div>
        )}
        {finalMessage && (
          <div className="mt-6 rounded-lg border-l-4 border-violet-400 bg-violet-50 p-4">
            {finalMessage.imageData ? (
              <div className="flex flex-col gap-2">
                {finalMessage.body && <p className="mb-2">{finalMessage.body}</p>}
                <img
                  src={`data:image/png;base64,${finalMessage.imageData.data}`}
                  alt="Sales Graph"
                  className="rounded-lg shadow-md max-w-full h-auto"
                />
              </div>
            ) : (
              <p>{finalMessage.body}</p>
            )}
          </div>
        )}
      </div>

      {loading && (
        <div className="mt-4 w-full max-w-md rounded-lg border border-blue-300 bg-blue-100 p-4 text-blue-800 shadow">
          <p className="font-medium">Streaming response...</p>
        </div>
      )}

      {successMessage && !loading && !errorMessage && (
        <div
          className={`mt-4 w-full max-w-md rounded-lg border border-green-300 bg-green-100 p-4 text-green-800 shadow transition-opacity duration-1000 ${
            showSuccess ? 'opacity-100' : 'opacity-0'
          }`}
        >
          <p className="font-medium">{successMessage}</p>
        </div>
      )}

      {errorMessage && !loading && (
        <div
          className={`mt-4 w-full max-w-md rounded-lg border border-red-300 bg-red-100 p-4 text-red-800 shadow transition-opacity duration-1000 ${
            showError ? 'opacity-100' : 'opacity-0'
          }`}
        >
          <p className="font-medium">{errorMessage}</p>
        </div>
      )}
    </div>
  );
};

export default Chatbot;
