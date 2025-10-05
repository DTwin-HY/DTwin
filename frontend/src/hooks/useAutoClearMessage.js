import { useState, useEffect } from 'react';

export const useAutoClearMessage = (message, setMessage, delay = 5000) => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!message) return;

    setVisible(true);

    const timer = setTimeout(() => {
      setVisible(false);
      setMessage('');
    }, delay);

    return () => clearTimeout(timer);
  }, [message, setMessage, delay]);

  return visible;
};
