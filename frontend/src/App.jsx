import { useState } from "react";
import "./index.css";

const App = () => {
  const [inputValue, setInputValue] = useState("");
  const [result, setResult] = useState("");

  const pingBackend = async () => {
    const res = await fetch("http://localhost:5000/api/ping");
    const data = await res.json();
    console.log(data);
  };

  pingBackend();
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue) return;

    try {
      const res = await fetch("http://localhost:5000/api/echo", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: inputValue }),
      });

      if (!res.ok) {
        throw new Error("Failed to send data");
      }

      const data = await res.json();
      setResult(data.you_sent.message);
      setInputValue("");
    } catch (err) {
      console.error(err);
      setResult("Error connecting to backend");
    }
  };

  return (
    <div className="">
      <form onSubmit={handleSubmit} className="">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          className=""
        />

        <button type="submit" className="">
          Submit
        </button>
      </form>

      {result && (
        <div className="">
          <p className="">{result}</p>
        </div>
      )}
    </div>
  );
};

export default App;
