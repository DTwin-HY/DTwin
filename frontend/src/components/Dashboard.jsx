import { useState, useEffect } from 'react';
import { fetchDashboardData } from '../api/dashboardapi';
import MetricCard from './MetricCard';
import { ChevronUp, ChevronDown } from 'lucide-react';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState({});
  const [stageCompact, setStageCompact] = useState(true);
  const [_, setAnimatingCompact] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const data = await fetchDashboardData();
        setDashboardData(data || {});
      } catch (err) {
        console.error('Failed to fetch dashboard data', err);
      }
    })();
  }, []);

  const sales = dashboardData.sales || {};
  const revenue = dashboardData.revenue || {};
  const transactions = dashboardData.transactions || {};

  const toggleCompact = () => {
    setAnimatingCompact(true);

    setTimeout(() => {
      setStageCompact((s) => !s);
    }, 150);

    setTimeout(() => {
      setAnimatingCompact(false);
    }, 300);
  };

  return (
    <div className="w-full bg-white transition-all duration-300 ease-in-out">
      <div className="rounded-2xl border border-slate-200 backdrop-blur-md transition-all duration-300">
        <div className="flex items-center justify-between p-6">
          <div>
            <h2 className="text-2xl font-bold text-[#222F68]">Analytics Dashboard</h2>
            <p className="text-md mt-1 text-[#070b11]">Real-time performance metrics</p>
          </div>

          <div className="flex items-center gap-2">
            <button
              aria-label="collapse dashboard"
              className="rounded-lg px-3 py-2 text-slate-600 transition-colors hover:cursor-pointer hover:bg-slate-100 hover:text-slate-800"
              onClick={toggleCompact}
            >
              {stageCompact ? (
                <ChevronDown className="h-5 w-5" />
              ) : (
                <ChevronUp className="h-5 w-5" />
              )}
            </button>
          </div>
        </div>

        <div
          className={`grid gap-4 p-6 transition-all duration-300 ease-in-out ${
            stageCompact ? 'grid-cols-1 md:grid-cols-3' : 'grid-cols-1 md:grid-cols-3'
          }`}
        >
          {/* Sales → blue (like Sales (Units) in SalesCard) */}
          <MetricCard
            title="Sales"
            metric={sales}
            compact={stageCompact}
            color="#2563eb" // blue-600
            dotOutlineColor="#2563eb"
          />

          {/* Transactions → purple */}
          <MetricCard
            title="Transactions"
            metric={transactions}
            compact={stageCompact}
            color="#7c3aed" // purple-600
            dotOutlineColor="#7c3aed"
          />

          {/* Revenue → green (like Revenue in SalesCard) */}
          <MetricCard
            title="Revenue"
            metric={revenue}
            compact={stageCompact}
            color="#16a34a" // green-600
            dotOutlineColor="#16a34a"
          />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
