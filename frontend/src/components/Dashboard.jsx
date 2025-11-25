import { useState, useEffect } from 'react';
import { fetchDashboardData } from '../api/dashboardapi';
import MetricCard from './MetricCard';
import { Pin, PinOff, ChevronUp, ChevronDown } from 'lucide-react';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState({});
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isPinned, setIsPinned] = useState(false);
  const [stageCompact, setStageCompact] = useState(false);
  const [animatingCompact, setAnimatingCompact] = useState(false);

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
    <div
      className={`w-full transition-all duration-300 ease-in-out ${
        isPinned ? 'sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200 shadow-md' : ''
      }`}
    >
      <div className="bg-gradient-to-r from-slate-50 to-blue-50 border border-gray-200 rounded-lg shadow-sm overflow-hidden">
        <div className="p-4 border-b border-gray-100 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-800">Analytics Dashboard</h2>
            <p className="text-sm text-gray-500 mt-1">Real-time performance metrics</p>
          </div>

          <div className="flex items-center gap-1">
            <button
              aria-label="pin dashboard"
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-600 hover:text-gray-900"
              onClick={() => setIsPinned((s) => !s)}
            >
              {isPinned ? <PinOff className="w-5 h-5" /> : <Pin className="w-5 h-5" />}
            </button>

            <button
              aria-label="collapse dashboard"
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-600 hover:text-gray-900"
              onClick={() => setIsCollapsed((s) => !s)}
            >
              {isCollapsed ? <ChevronDown className="w-5 h-5" /> : <ChevronUp className="w-5 h-5" />}
            </button>

            <button
              aria-label="toggle compact"
              className="px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors text-sm font-medium text-gray-600 hover:text-gray-900"
              onClick={toggleCompact}
            >
              {stageCompact ? 'Full' : 'Compact'}
            </button>
          </div>
        </div>

        <div
          className={`
            grid gap-4 transition-all duration-300 ease-in-out
            ${animatingCompact ? 'opacity-0' : 'opacity-100'}
            ${isCollapsed ? 'max-h-0 p-0 opacity-0' : 'max-h-[900px] p-4'}
            ${stageCompact ? 'grid-cols-1 md:grid-cols-3' : 'md:grid-cols-3'}
          `}
        >
          <MetricCard title="Sales" metric={sales} compact={stageCompact} color="hsl(220 90% 56%)" dotOutlineColor="#1E3A8A"/>
          <MetricCard title="Transactions" metric={transactions} compact={stageCompact} color="hsl(140 60% 40%)" dotOutlineColor="#166534" />
          <MetricCard title="Revenue" metric={revenue} compact={stageCompact} color="hsl(30 90% 50%)" dotOutlineColor="#9A3412"/>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
