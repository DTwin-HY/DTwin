import axios from './axiosInstance';

export const sendMessage = async (message) => {
  const res = await axios.post('/api/supervisor', { message });
  return res.data;
};
