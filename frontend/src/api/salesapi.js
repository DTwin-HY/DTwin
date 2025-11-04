const VITE_BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export const fetchSalesData = async (startDate, endDate) => {
  try {
    const res = await fetch(
      `${VITE_BACKEND_URL}/api/sales-data?start_date=${startDate}&end_date=${endDate}`,
      {
        credentials: 'include',
      },
    );

    if (!res.ok) {
      throw new Error(`Failed to fetch sales data: ${res.status}`);
    }

    const data = await res.json();
    return data;
  } catch (err) {
    console.error('Error fetching sales data:', err);
    throw err;
  }
};
