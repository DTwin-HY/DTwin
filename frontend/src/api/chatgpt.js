import axios from './axiosInstance';

export const sendMessage = async (message) => {
  const res = await axios.post('/api/supervisor', { message });
  return res.data;
};

export const streamMessage = async (message, onChunk) => {
  const res = await fetch("http://localhost:5000/api/supervisor", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
    credentials: "include",
  });

  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop();

    for (const part of parts) {
      if (part.startsWith("data: ")) {
        const jsonData = part.slice(6);
        try {
          const chunk = JSON.parse(jsonData);

          // Now chunk is an array of updates (structured object)
          if (Array.isArray(chunk)) {
            onChunk(chunk); // Pass the structured chunk to the callback
          } else if (chunk.done) {
            onChunk({ done: true, reply: chunk.reply });
          }
        } catch (err) {
          console.error("JSON parse error:", err);
        }
      }
    }
  }
};