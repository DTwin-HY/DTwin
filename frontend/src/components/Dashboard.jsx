import { useState, useEffect } from 'react';
import { fetchDashboardData } from '../api/dashboardapi';
import MetricCard from './MetricCard';
import { Pin, PinOff, ChevronUp, ChevronDown } from 'lucide-react';

const mapSeries = (raw) => {
  if (!raw) return null;
  // raw is expected to be an object like {0: val, 1: val, ...}
  const keys = Object.keys(raw).sort((a, b) => Number(a) - Number(b));
  return keys.map((k, i) => ({ name: String(k), value: raw[k] }));
};

const buildMetricRows = (metricData) => {
  if (!metricData) return [];
  return [
    {
      label: 'Current quarter',
      amount: metricData.current_quarter?.amount,
      growth: metricData.current_quarter?.growth,
      series: mapSeries(metricData.raw_graph_data?.current_quarter),
    },
    {
      label: 'Previous quarter',
      amount: metricData.previous_quarter?.amount,
      growth: metricData.previous_quarter?.growth,
      series: mapSeries(metricData.raw_graph_data?.previous_quarter),
    },
    {
      label: 'YTD',
      amount: metricData.ytd?.amount,
      growth: metricData.ytd?.growth,
      series: mapSeries(metricData.raw_graph_data?.ytd),
    },
  ];
};

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState({});
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isPinned, setIsPinned] = useState(false);
  const [isCompact, setIsCompact] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const data = await fetchDashboardData();
        console.log('fetchDashboardData ->', data);
        setDashboardData(data || {});
      } catch (err) {
        console.error('Failed to fetch dashboard data', err);
      }
    })();
  }, []);


  const sales = dashboardData.sales || {};
  const revenue = dashboardData.revenue || {};
  const transactions = dashboardData.transactions || {};

  return (
    <div
      className={`w-full transition-all duration-300 ease-in-out ${
        isPinned ? 'sticky top-0 z-50 bg-background/95 backdrop-blur-sm border-b border-border' : ''
      }`}
    >
      <div className="p-3 bg-card/50 border border-border/50 rounded-md">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold">Analytics Dashboard</h2>
          <div className="flex items-center gap-2">
            <button
              aria-label="pin dashboard"
              className="p-2 rounded hover:bg-muted"
              onClick={() => setIsPinned((s) => !s)}
            >
              {isPinned ? <PinOff className="w-4 h-4" /> : <Pin className="w-4 h-4" />}
            </button>
            <button
              aria-label="collapse dashboard"
              className="p-2 rounded hover:bg-muted"
              onClick={() => setIsCollapsed((s) => !s)}
            >
              {isCollapsed ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
            </button>
            <button
              aria-label="toggle compact"
              className="p-2 rounded hover:bg-muted"
              onClick={() => setIsCompact((s) => !s)}
            >
              <span className="sr-only">Toggle compact</span>
              {isCompact ? 'Compact' : 'Full'}
            </button>
          </div>
        </div>

        

        <div
          className={`grid gap-4 transition-all duration-300 ease-in-out ${
            isCollapsed ? 'max-h-0 p-0 opacity-0' : 'max-h-[900px] opacity-100 p-0'
          } ${isCompact ? 'grid-cols-1 md:grid-cols-3' : 'md:grid-cols-3'}`}
        >
        </div>
      </div>
    </div>
  );
};

export default Dashboard;