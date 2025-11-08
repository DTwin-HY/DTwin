import axios from './axiosInstance';

const VITE_BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export const fetchSalesData = async (startDate, endDate) => {
  try {
    const res = await axios.get(`${VITE_BACKEND_URL}/api/sales-data`, {
      params: {
        start_date: startDate,
        end_date: endDate,
      },
      withCredentials: true,
    });

    return res.data;
  } catch (err) {
    console.error('Error fetching sales data:', err);
    throw err;
  }
};
