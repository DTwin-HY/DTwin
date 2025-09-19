import axios from './axiosInstance';

export const signup = async ({ username, password }) => {
  const { data } = await axios.post('/api/signup', { username, password });
  return data;
};

export const signin = async ({ username, password }) => {
  const { data } = await axios.post('/api/signin', { username, password });
  return data;
};

export const signout = async () => {
  const { data } = await axios.post('/api/logout');
  return data;
};
