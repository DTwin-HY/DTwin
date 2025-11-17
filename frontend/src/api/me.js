import axios from './axiosInstance';

export const fetchMe = async () => {
  const res = await axios.get('/api/me');
  return res.data;
};
