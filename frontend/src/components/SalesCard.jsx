import { useState, useEffect } from 'react';
import { TrendingUp, Users, Euro } from 'lucide-react';

const SalesCard = () => {
  const [period, setPeriod] = useState('daily');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  // Helper to format Date to yyyy-mm-dd
  const formatDate = (date) => date.toISOString().split('T')[0];

  // Update calendar based on buttons
  useEffect(() => {
    const today = new Date();
    if (period === 'daily') {
      setStartDate(formatDate(today));
      setEndDate(formatDate(today));
    } else if (period === 'weekly') {
      const dayOfWeek = today.getDay();
      const start = new Date(today);
      start.setDate(today.getDate() - dayOfWeek);

      const end = new Date(start);
      end.setDate(start.getDate() + 6);

      setStartDate(formatDate(start));
      setEndDate(formatDate(end));
    } else if (period === 'yearly') {
      const start = new Date(today.getFullYear(), 0, 1);
      const end = new Date(today.getFullYear(), 11, 31);
      setStartDate(formatDate(start));
      setEndDate(formatDate(end));
    }
  }, [period]);

  const getSalesData = () => {
    // TODO: muokkaa oikeeks api kutsuks
    const random = () => Math.floor(Math.random() * 1000);
    return {
      sales: random(),
      revenue: random() * 15,
      customers: random() / 2,
    };
  };

  const data = getSalesData();

  return (
    <div className="flex min-h-screen flex-col items-center justify-start p-6">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-lg">
        <h2 className="mb-4 text-2xl font-bold text-gray-900">Sales Overview</h2>

        <div className="mb-4 flex gap-3">
          {['daily', 'weekly', 'yearly'].map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
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

        <div className="space-y-4">
          <div className="flex items-center justify-between rounded-xl bg-green-50 p-4">
            <div className="flex items-center gap-3">
              <Euro className="text-green-600" size={22} />
              <p className="font-medium text-gray-700">Revenue (€)</p>
            </div>
            <p className="text-lg font-semibold text-gray-900">{data.revenue}</p>
          </div>

          <div className="flex items-center justify-between rounded-xl bg-blue-50 p-4">
            <div className="flex items-center gap-3">
              <TrendingUp className="text-blue-600" size={22} />
              <p className="font-medium text-gray-700">Sales (Units)</p>
            </div>
            <p className="text-lg font-semibold text-gray-900">{data.sales}</p>
          </div>

          <div className="flex items-center justify-between rounded-xl bg-purple-50 p-4">
            <div className="flex items-center gap-3">
              <Users className="text-purple-600" size={22} />
              <p className="font-medium text-gray-700">Customers</p>
            </div>
            <p className="text-lg font-semibold text-gray-900">{Math.floor(data.customers)}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SalesCard;
