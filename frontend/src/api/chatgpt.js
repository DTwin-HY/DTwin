import axios from './axiosInstance';

export const sendMessage = async (message) => {
  const res = await axios.post('/api/echo', { message });
  return res.data;
};

export const fetchSalesByDate = async ({ date }) => {
  const res = await axios.get('/api/sales', { params: { date } });
  return res.data;
};

export const simulateSalesForDate = async ({ date, lat, lon }) => {
  const res = await axios.post('/api/simulate-sales', { date, lat: Number(lat), lon: Number(lon) });
  return res.data;
};

export const fetchWeather = async (location) => {
  const res = await axios.post('/api/weather', location);
  console.log('chatgpt.js: ', res.data);
  return res.data;
};
