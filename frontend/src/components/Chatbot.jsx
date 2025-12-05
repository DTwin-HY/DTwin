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

const PHRASES = ['sales development?', 'warehouse inventory?', 'other company related things?'];

const Chatbot = () => {
  const [inputValue, setInputValue] = useState('');
  const [responses, setResponses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [chats, setChats] = useState([]);
  const [threadId, setThreadId] = useState(null);
  const [userId, setUserId] = useState(null);

  const [placeholderSuffix, setPlaceholderSuffix] = useState('');
  const [phraseIndex, setPhraseIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const currentPhrase = PHRASES[phraseIndex];

    if (!isDeleting && placeholderSuffix === currentPhrase) {
      const timeout = setTimeout(() => setIsDeleting(true), 2000);
      return () => clearTimeout(timeout);
    }

    if (isDeleting && placeholderSuffix === '') {
      setIsDeleting(false);
      setPhraseIndex((prev) => (prev + 1) % PHRASES.length);
      return;
    }

    const timeout = setTimeout(
      () => {
        setPlaceholderSuffix((prev) => {
          if (isDeleting) {
            return prev.slice(0, -1);
          }
          return currentPhrase.slice(0, prev.length + 1);
        });
      },
      isDeleting ? 50 : 100,
    );

    return () => clearTimeout(timeout);
  }, [placeholderSuffix, isDeleting, phraseIndex]);

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

    const messageToSend = inputValue;
    setInputValue('');

    finalizedRef.current = false;
    setLoading(true);
    setSuccessMessage('');
    setErrorMessage('');
    setResponses([]);
    setChats((prevChats) => [{ role: 'user', message: messageToSend }, ...(prevChats || [])]);

    try {
      await streamMessage(
        messageToSend,
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
    <div className="w-full max-w-full">
      <div className="relative rounded-2xl border border-slate-200 bg-white p-6 shadow-lg">
        <div className="group absolute top-6 right-6">
          <button
            type="button"
            onClick={handleNewChat}
            disabled={loading || userId === null}
            className="flex items-center justify-center rounded-lg transition-colors duration-200 hover:cursor-pointer hover:opacity-80 disabled:opacity-50"
            style={{ color: '#1f2937' }}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-8 w-8"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
              <circle cx="18" cy="6" r="5" fill="#ffffff" stroke="currentColor" strokeWidth={1} />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M18 3.5v5M15.5 6h5"
                stroke="currentColor"
                strokeWidth={1}
              />
            </svg>
          </button>

          <div
            className="pointer-events-none absolute right-0 bottom-full mb-2 rounded-md px-3 py-1.5 text-xs whitespace-nowrap opacity-0 shadow-lg transition-opacity duration-200 group-hover:opacity-100"
            style={{ backgroundColor: 'rgba(0,0,0,0.8)', color: '#ffffff' }}
          >
            Start a new chat
          </div>
        </div>

        <h3 className="mb-6 bg-clip-text text-center text-4xl leading-relaxed font-bold text-[#222F68]">
          Your Digital Twin Assistant
        </h3>

        <ListMessages messages={chats} />

        {loading && (
          <div className="mt-4 flex justify-center">
            <div className="flex h-12 items-center justify-center gap-2">
              {[...Array(3)].map((_, i) => (
                <span
                  key={i}
                  className="dot-base animate-bounce-colorwave h-6 w-6 rounded-full"
                  style={{ animationDelay: `${i * 0.2}s` }}
                ></span>
              ))}
            </div>
          </div>
        )}

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

        <form onSubmit={handleSubmit} className="mt-4">
          <div className="relative flex items-center">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={loading || userId === null}
              className="w-full resize-none rounded-full border py-4 pr-16 pl-6 text-base focus:ring-2 focus:outline-none"
              style={{
                borderColor: '#d1d5db',
                backgroundColor: 'rgba(255, 255, 255, 0.7)',
                color: '#1f2937',
              }}
              placeholder={
                userId === null ? 'Loading user...' : `Ask me about ${placeholderSuffix}`
              }
              rows={1}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
            />

            <button
              type="submit"
              disabled={loading || userId === null || !inputValue.trim()}
              className="absolute right-2 flex h-11 w-11 items-center justify-center rounded-full text-sm font-medium transition-colors duration-200 hover:cursor-pointer disabled:opacity-40"
              style={{
                backgroundColor: 'hsl(263 70% 60%)',
              }}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
              </svg>
            </button>
          </div>
        </form>

        {/* Success and error messages */}
        {successMessage && !loading && !errorMessage && (
          <div className="mt-4 flex justify-center">
            <div
              className={`w-full max-w-md rounded-lg border p-4 text-sm shadow transition-opacity duration-1000 ${
                showSuccess ? 'opacity-100' : 'opacity-0'
              }`}
              style={{
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                color: '#10b981',
              }}
            >
              <p className="font-medium">{successMessage}</p>
            </div>
          </div>
        )}
        {errorMessage && !loading && (
          <div className="mt-4 flex justify-center">
            <div
              className={`w-full max-w-md rounded-lg border p-4 text-sm shadow transition-opacity duration-1000 ${
                showError ? 'opacity-100' : 'opacity-0'
              }`}
              style={{
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                color: '#ef4444',
              }}
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
