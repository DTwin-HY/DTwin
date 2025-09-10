import { useEffect, useState } from "react";
import "../index.css";
import { sendMessage } from "../api/chatgpt";
import { signout } from "../api/auth";
import { useNavigate } from "react-router-dom"; 

const Home = () => {
  const [inputValue, setInputValue] = useState("");
  const [userMessage, setUserMessage] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(""), 5000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) {
      setErrorMessage("Syöte ei voi olla tyhjä.");
      return;
    }

    setLoading(true);
    setSuccessMessage("");
    setErrorMessage("");
    setResponse("");

    try {
      const data = await sendMessage(inputValue);
      setUserMessage(inputValue);
      setResponse(data.message);
      setSuccessMessage("Prompt and response saved to database!");
      setInputValue("");
    } catch (err) {
      console.error(err);
      setErrorMessage(`Error in the backend/database${err?.message ? `: ${err.message}` : ""}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
    try {
      await signout();
      navigate("/signin");
    } catch (err) {
      console.error("Error during sign out:", err);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="w-full max-w-md mb-4">
        <button
          onClick={handleSignOut}
          disabled={loading}
          className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg shadow hover:bg-gray-800 transition-colors duration-200 disabled:opacity-60"
        >
          Logout
        </button>
      </div>
    <img
      src="/vttlogo.png" 
      alt="Logo" 
      className="w-85 h-35 mb-5 ml-[45px] rounded-full"
    />

      <form onSubmit={handleSubmit} className="flex flex-col gap-4 w-full max-w-md bg-white p-6 rounded-xl shadow-md">

        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          disabled={loading}
          className="border border-gray-300 rounded-lg p-4 text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Type your message..."
        ></textarea>
        <button type="submit" disabled={loading} className="bg-blue-500 text-white font-semibold py-3 rounded-lg shadow hover:bg-blue-600 transition-colors duration-200">
          Submit
        </button>
      </form>

      {loading && (
        <div className="mt-4 w-full max-w-md p-4 rounded-lg border border-blue-300 bg-blue-100 text-blue-800 shadow">
          <p className="font-medium">Loading answer...</p>
        </div>
      )}

      {successMessage && !loading && !errorMessage && (
        <div className="mt-4 w-full max-w-md p-4 rounded-lg border border-green-300 bg-green-100 text-green-800 shadow">
          <p className="font-medium">{successMessage}</p>
        </div>
      )}

      {errorMessage && !loading && (
        <div className="mt-4 w-full max-w-md p-4 rounded-lg border border-red-300 bg-red-100 text-red-800 shadow">
          <p className="font-medium">{errorMessage}</p>
        </div>
      )}

      {userMessage && (
        <div className="mt-6 bg-blue-100 p-4 rounded-lg shadow max-w-2xl w-full break-words">
          <p className="text-blue-800 font-medium text-xl">Your message:</p>
          <p className="text-gray-700 text-xl">{userMessage}</p>
        </div>
      )}

      {response && (
        <div className="mt-4 bg-green-100 p-4 rounded-lg shadow max-w-2xl w-full break-words">
          <p className="text-green-800 font-medium text-xl">Chatbot's response:</p>
          <p className="text-gray-700 text-xl">{response}</p>
        </div>
      )}
    </div>
  );
};

export default Home;
