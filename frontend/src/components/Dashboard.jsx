import { useState, useEffect } from 'react';
import { fetchDashboardData } from '../api/dashboardapi';
import MetricCard from './MetricCard';
import { ChevronUp, ChevronDown } from 'lucide-react';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState({});
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [stageCompact, setStageCompact] = useState(true);

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
    <div className="w-full transition-all duration-300 ease-in-out">
      <div className="bo rounded-2xl border border-[hsl(var(--accent))]/30 shadow-sm transition-all duration-300">
        <div className="flex items-center justify-between p-4">
          <div>
            <h2 className="text-gradient text-2xl font-bold">Analytics Dashboard</h2>
            <p className="mt-1 text-lg text-gray-500">Real-time performance metrics</p>
          </div>

          <div className="flex items-center gap-1">
            <button
              aria-label="collapse dashboard"
              className="rounded-lg p-2 text-[hsl(var(--foreground))]/60 transition-colors hover:bg-white/5"
              onClick={() => setIsCollapsed((s) => !s)}
            >
              {isCollapsed ? (
                <ChevronDown className="h-5 w-5" />
              ) : (
                <ChevronUp className="h-5 w-5" />
              )}
            </button>

            <button
              aria-label="toggle compact"
              className="rounded-lg px-3 py-2 text-lg font-medium text-[hsl(var(--foreground))]/60 transition-colors hover:bg-white/5"
              onClick={toggleCompact}
            >
              {stageCompact ? 'Full' : 'Compact'}
            </button>
          </div>
        </div>

        <div
          className={`grid gap-4 p-4 ${stageCompact ? 'grid-cols-1 md:grid-cols-3' : 'md:grid-cols-3'}`}
          style={{
            maxHeight: isCollapsed ? '0' : '1000px',
            opacity: isCollapsed ? 0 : 1,
            overflow: 'hidden',
            transition: 'max-height 0.3s ease, opacity 0.3s ease, padding 0.3s ease',
            paddingTop: isCollapsed ? '0' : '1rem',
            paddingBottom: isCollapsed ? '0' : '1rem',
          }}
        >
          <MetricCard
            title="Sales"
            metric={sales}
            compact={stageCompact}
            color="hsl(220 90% 56%)"
            dotOutlineColor="#3a5cb8ff"
          />
          <MetricCard
            title="Transactions"
            metric={transactions}
            compact={stageCompact}
            color="hsl(140 60% 40%)"
            dotOutlineColor="#0d893dff"
          />
          <MetricCard
            title="Revenue"
            metric={revenue}
            compact={stageCompact}
            color="hsl(30 90% 50%)"
            dotOutlineColor="#c96717ff"
          />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
