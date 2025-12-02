import { useState, useEffect } from 'react';
import { fetchDashboardData } from '../api/dashboardapi';
import MetricCard from './MetricCard';
import { ChevronUp, ChevronDown } from 'lucide-react';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState({});
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [stageCompact, setStageCompact] = useState(true);
  const [animatingCompact, setAnimatingCompact] = useState(false); // eslint-disable-line

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
      <div className="bo rounded-2xl border shadow-sm transition-all duration-300" style={{ borderColor: '#e5e7eb', background: 'linear-gradient(135deg, #e6eaf8ff 0%, #ffffffff 50%, #fcf8ffff 100%)' }}>
        <div className="flex items-center justify-between p-4">
          <div>
            <h2 className="text-3xl font-extrabold leading-relaxed bg-clip-text text-transparent" style={{ backgroundImage: 'linear-gradient(to right, #383054ff, #514475ff, #776c97ff)' }} >Analytics Dashboard</h2>
            <p className="mt-1 text-xl font-semibold" style={{ color: '#000000ff' }}>Real-time performance metrics</p>
          </div>

          <div className="flex items-center gap-1">
            <button
              aria-label="collapse dashboard"
              className="rounded-lg p-2 transition-colors"
              style={{ color: '#000000ff' }}
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
              className="rounded-lg px-3 py-2 text-xl font-medium transition-colors"
              style={{ color: '#000000ff' }}
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
            color="hsla(280, 71%, 59%, 1.00)"
            dotOutlineColor="#8247b6ff"
          />
          <MetricCard
            title="Revenue"
            metric={revenue}
            compact={stageCompact}
            color="hsla(198, 90%, 50%, 1.00)"
            dotOutlineColor="#194aa5ff"
          />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
