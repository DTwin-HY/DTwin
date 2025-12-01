import axios from './axiosInstance';

const VITE_BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export const fetchDashboardData = async () => {
  try {
    const res = await axios.get(`${VITE_BACKEND_URL}/api/dashboard-data`, {
      withCredentials: true,
    });

    return res.data;
  } catch (err) {
    console.error('Error fetching dashboard data:', err);
    throw err;
  }
};
