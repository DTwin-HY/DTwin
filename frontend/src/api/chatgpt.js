import axios from './axiosInstance';

const VITE_BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export const sendMessage = async (message) => {
  const res = await axios.post('/api/supervisor', { message });
  return res.data;
};

export const fetchChats = async () => {
  const res = await axios.get('/api/fetch_chats');
  return res.data;
};

export const streamMessage = async (message, threadId, onChunk, onThreadId) => {
  const res = await fetch(`${VITE_BACKEND_URL}/api/supervisor`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, thread_id: threadId || null }),
    credentials: 'include',
  });

  if (!res.ok) {
    throw new Error(`Request failed with status ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split('\n\n');
    buffer = parts.pop();

    for (const rawPart of parts) {
      const part = rawPart.trim();
      if (!part) continue;
      // Voidaan saada:
      // 1) event: thread_id \n data: {...}
      // 2) data: {...}
      const lines = part.split('\n');
      let eventType = 'message';
      let dataLine = null;

      for (const line of lines) {
        if (line.startsWith('event:')) {
          eventType = line.slice('event:'.length).trim();
        } else if (line.startsWith('data:')) {
          dataLine = line.slice('data:'.length).trim();
        }
      }

      if (!dataLine) continue;
      let payload;
      try {
        payload = JSON.parse(dataLine);
      } catch (err) {
        console.error('JSON parse error:', err, dataLine);
        continue;
      }

      if (eventType === 'thread_id') {
        if (onThreadId && payload.thread_id) {
          onThreadId(payload.thread_id);
        }
        continue;
      }

      const chunk = payload;

      if (Array.isArray(chunk)) {
        onChunk(chunk);
      } else if (chunk && chunk.done) {
        onChunk({ done: true, reply: chunk.reply });
      } else {
        onChunk(chunk);
      }
    }
  }
};
