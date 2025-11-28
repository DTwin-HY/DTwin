import { useState, useRef, useEffect } from 'react';
import { streamMessage } from '../api/chatgpt';
import { fetchMe } from '../api/me';
import { useAutoClearMessage } from '../hooks/useAutoClearMessage';
import StepCard from './StepCard';
import ListMessages from './ListMessages';
import { headerLine } from '../utils/streamFormat';
import {
  getThreadIdForUser,
  setThreadIdForUser,
  clearThreadIdForUser,
} from '../utils/threadCookie';

const Chatbot = () => {
  const [inputValue, setInputValue] = useState('');
  const [responses, setResponses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [chats, setChats] = useState([]);
  const [threadId, setThreadId] = useState(null);
  const [userId, setUserId] = useState(null);

  const finalizedRef = useRef(false); // Prevent double-finalize

  useEffect(() => {
    const initUserAndThread = async () => {
      try {
        const data = await fetchMe();
        // eqeqeq-yhteensopiva tapa tarkistaa, että user_id ei ole null/undefined
        if (data && data.user_id !== null && data.user_id !== undefined) {
          setUserId(data.user_id);
          const savedThreadId = getThreadIdForUser(data.user_id);
          if (savedThreadId) {
            console.log('Loaded threadId for user from cookie:', savedThreadId);
            setThreadId(savedThreadId);
          }
        }
      } catch (err) {
        console.error('Failed to load /api/me', err);
      }
    };

    initUserAndThread();
  }, []);

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

      setChats((prevChats) => [
        { role: 'supervisor', steps, finalMessage: last.body },
        ...(prevChats || []),
      ]);
      console.log('Updated chats:', chats);
      return steps;
    });
  };

  const handleNewChat = () => {
    finalizedRef.current = false;
    if (userId !== null) {
      clearThreadIdForUser(userId);
    }
    setThreadId(null);
    setResponses([]);
    setSuccessMessage('');
    setErrorMessage('');
    setChats([]);
  };

  const handleSubmit = async (e) => {
    console.log('Submitting message:', inputValue);
    e.preventDefault();
    if (!inputValue.trim()) {
      setErrorMessage('Input cannot be empty');
      return;
    }
    finalizedRef.current = false;
    setLoading(true);
    setSuccessMessage('');
    setErrorMessage('');
    setResponses([]);
    setChats((prevChats) => [...(prevChats || []), { role: 'user', message: inputValue }]);

    try {
      await streamMessage(
        inputValue,
        threadId,
        (chunk) => {
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
          setThreadId((prev) => {
            const effective = prev || newThreadId;
            if (userId !== null) {
              setThreadIdForUser(userId, effective);
            }
            return effective;
          });
        },
      );
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
        <h3 className="mb-4 text-lg font-semibold text-gray-800">Ask the DTwin assistant</h3>
          <ListMessages messages={chats} />
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

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={loading || userId === null}
            className="min-h-[100px] rounded-lg border border-gray-300 p-4 text-lg focus:ring-2 focus:ring-purple-500 focus:outline-none"
            placeholder={userId === null ? 'Loading user...' : 'Type your message...'}
          />
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={loading || userId === null}
              className="flex-1 rounded-lg bg-purple-500 py-3 font-semibold text-white shadow transition-colors duration-200 hover:bg-purple-600 disabled:bg-gray-400"
            >
              {loading ? 'Streaming...' : 'Send Message'}
            </button>
            <button
              type="button"
              onClick={handleNewChat}
              disabled={loading || userId === null}
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


      </div>
    </div>
  );
};

export default Chatbot;
