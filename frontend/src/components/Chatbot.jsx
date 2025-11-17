import { useState, useRef } from 'react';
import { streamMessage } from '../api/chatgpt';
import { useAutoClearMessage } from '../hooks/useAutoClearMessage';
import StepCard from './StepCard';
import ListMessages from './ListMessages';
import { headerLine } from '../utils/streamFormat';

const Chatbot = () => {
  const [inputValue, setInputValue] = useState('');
  const [responses, setResponses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [chats, setChats] = useState([]);
  const [threadId, setThreadId] = useState(null);
  const finalizedRef = useRef(false); // Prevent double-finalize

  const showSuccess = useAutoClearMessage(successMessage, setSuccessMessage);
  const showError = useAutoClearMessage(errorMessage, setErrorMessage);

  const finalizeLastResponse = () => {
    console.log('Finalizing last response...', responses);
    setResponses((prev) => {
      if (finalizedRef.current) return; // Already finalized this turn
      finalizedRef.current = true;

      const last = prev[prev.length - 1];
      const steps = prev.slice(0, -1);
      console.log('Last message and steps:', last, steps);

      // append a compact chat object for history usage
      setChats((prevChats) => [
        ...(prevChats || []),
        { role: 'supervisor', finalMessage: last.body, steps: steps },
      ]);
      console.log('Updated chats:', chats);
      // keep steps in responses (you can clear if you prefer: return [])
      return steps;
    });
  };

  const handleNewChat = () => {
    finalizedRef.current = false;
    setThreadId(null);      // seuraava viesti → uusi uuid backendiin
    setResponses([]);       // tyhjennä tämän session stepit näytöstä
    setSuccessMessage('');
    setErrorMessage('');
    // HUOM: jätetään chats ennalleen, jos haluat säilyttää historiaa
    // Jos haluat tyhjentää myös historiacomponentin, lisää:
    setChats([]);
  };


  const handleSubmit = async (e) => {
    console.log('Submitting message:', inputValue);
    e.preventDefault();
    if (!inputValue.trim()) {
      setErrorMessage('Input cannot be empty');
      return;
    }
    finalizedRef.current = false; // Reset for new turn
    setLoading(true);
    setSuccessMessage('');
    setErrorMessage('');
    setResponses([]);
    setChats((prevChats) => [...(prevChats || []), { role: 'user', message: inputValue }]);

    try {
      await streamMessage(inputValue, threadId, (chunk) => {
        console.log('Received chunk:', chunk);
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
      },
      (newThreadId) => {
        // eka event streamista: talletetaan thread_id
        setThreadId((prev) => prev || newThreadId);
      }
    );
      //const latest = await fetchChats();
      //setChats(latest);
      setSuccessMessage('Prompt and response saved to database!');
      setInputValue('');
    } catch (err) {
      console.error(err);
      setErrorMessage(`Error in backend/database${err?.message ? `: ${err.message}` : ''}`);
    } finally {
      console.log('reached finally block');
      setLoading(false);
      finalizeLastResponse();
    }
  };
  return (
    <div className="w-full max-w-full p-6">
      <div className="rounded-xl bg-white p-6 shadow-md">
        <h3 className="mb-4 text-lg font-semibold text-gray-800">Ask the Supervisor</h3>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={loading}
              className="min-h-[100px] rounded-lg border border-gray-300 p-4 text-lg focus:ring-2 focus:ring-purple-500 focus:outline-none"
              placeholder="Type your message..."
            />
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 rounded-lg bg-purple-500 py-3 font-semibold text-white shadow transition-colors duration-200 hover:bg-purple-600 disabled:bg-gray-400"
              >
                {loading ? 'Streaming...' : 'Send Message'}
              </button>
              <button
                type="button"
                onClick={handleNewChat}
                disabled={loading}
                className="rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-100 disabled:opacity-50"
              >
                New chat
              </button>
            </div>
          </form>
        {loading && (
          <div className="mt-4 flex justify-center">
            <div className="w-full max-w-md rounded-lg border border-blue-300 bg-blue-100 p-4 text-blue-800 shadow">
              <p className="font-medium">Streaming response...</p>
            </div>
          </div>
        )}

        {/* Render message card for the latest response if loading=true*/}
        {loading &&
          responses.length > 0 &&
          (() => {
            const last = responses[responses.length - 1];
            return last ? (
              <StepCard
                key={responses.length - 1}
                title={last.title}
                content={last.body}
                imageData={last.imageData}
              />
            ) : null;
          })()}

        {successMessage && !loading && !errorMessage && (
          <div className="mt-4 flex justify-center">
            <div
              className={`w-full max-w-md rounded-lg border border-green-300 bg-green-100 p-4 text-green-800 shadow transition-opacity duration-1000 ${
                showSuccess ? 'opacity-100' : 'opacity-0'
              }`}
            >
              <p className="font-medium">{successMessage}</p>
            </div>
          </div>
        )}

        {errorMessage && !loading && (
          <div className="mt-4 flex justify-center">
            <div
              className={`w-full max-w-md rounded-lg border border-red-300 bg-red-100 p-4 text-red-800 shadow transition-opacity duration-1000 ${
                showError ? 'opacity-100' : 'opacity-0'
              }`}
            >
              <p className="font-medium">{errorMessage}</p>
            </div>
          </div>
        )}

        <ListMessages messages={chats} />
      </div>
    </div>
  );
};

export default Chatbot;
