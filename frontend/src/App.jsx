import { useState } from "react";
import "./index.css";

const App = () => {
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [result, setResult] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue) return;

    setLoading(true)
    setResult(""); 
    setMessage("Loading answer...")

    try {
      const res = await fetch("http://localhost:5000/api/echo", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: inputValue }),
      });

      if (!res.ok) {
        throw new Error(`Request failed: ${res.status}`);
      }

      const data = await res.json();
      console.log(data)
      setResult(data.message);
      setMessage("Prompt and answer saved into database!")
      setInputValue("");
    } catch (err) {
      console.error(err);
      setMessage(`Error in the backend/database${err?.message ? `: ${err.message}` : ""}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="">
      <form onSubmit={handleSubmit} className="">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          disabled={loading}
          className="border"
        />
        {/* button disabled when submitting */}
        <button type="submit" disabled={loading} className="">
          Submit
        </button>
      </form>
      {message && (
        <div className="">
          <p className="">{message}</p>
        </div>
      )}
      {result && (
        <div className="">
          <p className="">{result}</p>
        </div>
      )}
    </div>
  );
};

export default App;
