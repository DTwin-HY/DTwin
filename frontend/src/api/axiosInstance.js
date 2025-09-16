import axios from 'axios';

//const backendURL = process.env.VITE_BACKEND_URL;
const instance = axios.create({
  baseURL: process.env.VITE_BACKEND_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

export default instance;