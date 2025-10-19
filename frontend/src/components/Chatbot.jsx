import { useState } from 'react';
import { streamMessage } from '../api/chatgpt';
import { useAutoClearMessage } from '../hooks/useAutoClearMessage';

const Chatbot = () => {
  const [inputValue, setInputValue] = useState('');
  const [userMessage, setUserMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const showSuccess = useAutoClearMessage(successMessage, setSuccessMessage);
  const showError = useAutoClearMessage(errorMessage, setErrorMessage);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) {
      setErrorMessage('Input cannot be empty');
      return;
    }

    setLoading(true);
    setSuccessMessage('');
    setErrorMessage('');
    setResponse('');
    setUserMessage(inputValue);

    try {
      await streamMessage(inputValue, (chunk) => {
        if (Array.isArray(chunk)) {
          chunk.forEach((update) => {
            let text = `[${update.subgraph}] ${update.node}\n`;

            if (update.messages && update.messages.length) {
              update.messages.forEach((msg) => {
                const content = msg.content || "";
                const toolCalls = msg.tool_calls || [];

                if (content) text += `  ${content}\n`;
                if (toolCalls.length)
                  toolCalls.forEach((t) => (text += `  → ${t.name}()\n`));
              });
            }

            setResponse((prev) => prev + text + "\n");
          });
        }
      });

      setSuccessMessage('Prompt and response saved to database!');
      setInputValue('');
    } catch (err) {
      console.error(err);
      setErrorMessage(`Error in backend/database${err?.message ? `: ${err.message}` : ''}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-start bg-gray-100 p-4 pt-8">
      <div className="mt-4 w-[700px] rounded-xl bg-white p-6 shadow-md">
        <h3 className="mb-4 text-lg font-semibold text-gray-800">Chat with AI Assistant</h3>

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
          <div className="mt-6 rounded-lg border-l-4 border-blue-400 bg-blue-50 p-4">
            <p className="mb-1 font-medium text-blue-800">Your message:</p>
            <p className="whitespace-pre-wrap text-gray-700">{userMessage}</p>
          </div>
        )}

        {response && (
          <div className="mt-4 rounded-lg border-l-4 border-green-400 bg-green-50 p-4">
            <p className="mb-1 font-medium text-green-800">AI Response:</p>
            <p className="whitespace-pre-wrap text-gray-700">{response}</p>
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
