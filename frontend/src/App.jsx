import { useState } from "react";
import "./index.css";

const App = () => {
  const [inputValue, setInputValue] = useState("");
  const [result, setResult] = useState("");

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
      console.log(data)
      setResult(data.message);
      setInputValue("");
    } catch (err) {
      console.error(err);
      setResult("Error connecting to backend");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">

    <img
      src="/vttlogo.png" 
      alt="Logo" 
      className="w-85 h-35 mb-5 ml-[45px] rounded-full"
    />

      <form onSubmit={handleSubmit} className="flex flex-col gap-4 w-full max-w-md bg-white p-6 rounded-xl shadow-md">

        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          className="border border-gray-300 rounded-lg p-4 text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Type your message..."
        />

        <button type="submit" className="bg-blue-500 text-white font-semibold py-3 rounded-lg shadow hover:bg-blue-600 transition-colors duration-200">
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
