import { useState, useEffect } from 'react';
import { TrendingUp, Users, Euro, ChevronLeft, ChevronRight } from 'lucide-react';

const API_URL = import.meta.env.VITE_BACKEND_URL;

const SalesCard = () => {
  const [period, setPeriod] = useState('daily');
  const [offset, setOffset] = useState(0); // week/year offset
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [salesData, setSalesData] = useState({ revenue: 0, sales: 0, transactions: 0 });

  // Format Date to yyyy-mm-dd
  const formatDate = (date) => date.toISOString().split('T')[0];

  // Calculate date range based on period and offset
  useEffect(() => {
    const today = new Date();

    if (period === 'daily') {
      const target = new Date(today);
      target.setDate(today.getDate() + offset);
      setStartDate(formatDate(target));
      setEndDate(formatDate(target));
    }

    if (period === 'weekly') {
      const current = new Date(today);
      const mondayOffset = (current.getDay() + 6) % 7; // Monday = 0
      const monday = new Date(current);
      monday.setDate(current.getDate() - mondayOffset + offset * 7);

      const sunday = new Date(monday);
      sunday.setDate(monday.getDate() + 6);

      setStartDate(formatDate(monday));
      setEndDate(formatDate(sunday));
    }

    if (period === 'yearly') {
      const year = today.getFullYear() + offset;
      const start = new Date(year, 0, 1);
      const end = new Date(year, 11, 31);
      setStartDate(formatDate(start));
      setEndDate(formatDate(end));
    }
  }, [period, offset]);

  useEffect(() => {
    if (!startDate || !endDate || !API_URL) return;

    const fetchData = async () => {
      try {
        const res = await fetch(
          `${API_URL}/api/sales-data?start_date=${startDate}&end_date=${endDate}`,
        );
        const data = await res.json();
        setSalesData(data);
      } catch (err) {
        console.error('Error fetching sales data:', err);
      }
    };

    fetchData();
  }, [startDate, endDate, period]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-start p-6">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-lg">
        <h2 className="mb-4 text-2xl font-bold text-gray-900">Sales Overview</h2>

        {/* Period Selector */}
        <div className="mb-4 flex gap-3">
          {['daily', 'weekly', 'yearly'].map((p) => (
            <button
              key={p}
              onClick={() => {
                setPeriod(p);
                setOffset(0); // reset offset when changing period
              }}
              className={`flex-1 rounded-lg px-3 py-1 text-sm font-medium transition-colors ${
                period === p
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>

        {/* Date Navigation */}
        <div className="mb-4 flex items-center justify-between">
          <button
            onClick={() => setOffset((prev) => prev - 1)}
            className="rounded-lg bg-gray-100 p-2 hover:bg-gray-200"
          >
            <ChevronLeft className="text-gray-700" size={20} />
          </button>

          <div className="text-sm font-medium text-gray-700">
            {startDate} → {endDate}
          </div>

          <button
            onClick={() => setOffset((prev) => prev + 1)}
            className="rounded-lg bg-gray-100 p-2 hover:bg-gray-200"
          >
            <ChevronRight className="text-gray-700" size={20} />
          </button>
        </div>

        {/* Custom Range Inputs */}
        <div className="mb-6 flex gap-3">
          <input
            type="date"
            value={startDate}
            onChange={(e) => {
              setStartDate(e.target.value);
              setPeriod('custom');
            }}
            className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-xs focus:ring-2 focus:ring-blue-400 focus:outline-none lg:text-sm"
          />
          <span className="self-center text-gray-500">to</span>
          <input
            type="date"
            value={endDate}
            onChange={(e) => {
              setEndDate(e.target.value);
              setPeriod('custom');
            }}
            className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-xs focus:ring-2 focus:ring-blue-400 focus:outline-none lg:text-sm"
          />
        </div>

        {/* Data Cards */}
        <div className="space-y-4">
          <div className="flex items-center justify-between rounded-xl bg-green-50 p-4">
            <div className="flex items-center gap-3">
              <Euro className="text-green-600" size={22} />
              <p className="font-medium text-gray-700">Revenue (€)</p>
            </div>
            <p className="text-lg font-semibold text-gray-900">{salesData.revenue}</p>
          </div>

          <div className="flex items-center justify-between rounded-xl bg-blue-50 p-4">
            <div className="flex items-center gap-3">
              <TrendingUp className="text-blue-600" size={22} />
              <p className="font-medium text-gray-700">Sales (Units)</p>
            </div>
            <p className="text-lg font-semibold text-gray-900">{salesData.sales}</p>
          </div>

          <div className="flex items-center justify-between rounded-xl bg-purple-50 p-4">
            <div className="flex items-center gap-3">
              <Users className="text-purple-600" size={22} />
              <p className="font-medium text-gray-700">Transactions</p>
            </div>
            <p className="text-lg font-semibold text-gray-900">
              {Math.floor(salesData.transactions)}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SalesCard;
