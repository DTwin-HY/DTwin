import axios from 'axios';

console.log(import.meta.env.VITE_BACKEND_URL);
const instance = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

export default instance;