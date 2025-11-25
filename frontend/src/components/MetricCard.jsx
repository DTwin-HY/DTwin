import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip } from 'recharts';

const formatNumber = (num) => {
  if (num === null || num === undefined) return '—';
  if (Math.abs(num) >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (Math.abs(num) >= 1000) return `${(num / 1000).toFixed(1)}k`;
  return String(num);
};

const buildRowsFromMetric = (metric) => {
  if (!metric) return [];
  return [
    {
      label: 'Current quarter',
      amount: metric.current_quarter?.amount,
      growth: metric.current_quarter?.growth,
      series: metric.raw_graph_data ? metric.raw_graph_data.current_quarter : null,
    },
    {
      label: 'Previous quarter',
      amount: metric.previous_quarter?.amount,
      growth: metric.previous_quarter?.growth,
      series: metric.raw_graph_data ? metric.raw_graph_data.previous_quarter : null,
    },
    {
      label: 'YTD',
      amount: metric.ytd?.amount,
      growth: metric.ytd?.growth,
      series: metric.raw_graph_data ? metric.raw_graph_data.ytd : null,
    },
  ];
};

const buildCombinedSeries = (raw_graph_data) => {
  if (!raw_graph_data) return null;
  const idxs = Array.from(
    new Set([
      ...Object.keys(raw_graph_data?.current_quarter || {}),
      ...Object.keys(raw_graph_data?.previous_quarter || {}),
      ...Object.keys(raw_graph_data?.ytd || {}),
    ])
  ).sort((a, b) => Number(a) - Number(b));

  return idxs.map((k) => ({
    name: String(k),
    current: raw_graph_data.current_quarter?.[k] ?? null,
    previous: raw_graph_data.previous_quarter?.[k] ?? null,
    ytd: raw_graph_data.ytd?.[k] ?? null,
  }));
};

const seriesObjToArray = (obj) => {
  if (!obj) return null;
  return Object.keys(obj)
    .sort((a, b) => Number(a) - Number(b))
    .map((k) => ({ name: k, value: obj[k] }));
};

const FixedTooltipInside = ({ active, payload, coordinate }) => {
  if (!active || !payload || !payload.length) return null;
  if (!coordinate) return null;

  const { x, y } = coordinate;

  return (
    <div
      style={{
        position: 'absolute',
        left: x + 5,
        top: y - 30,
        background: 'rgba(255,255,255,0.9)',
        padding: '2px 6px',
        borderRadius: 4,
        fontSize: 12,
        pointerEvents: 'none',
        border: '1px solid rgba(0,0,0,0.1)',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      }}
    >
      {payload[0].value}
    </div>
  );
};

export const MetricCard = ({ title, metric = null, compact = false, color = '#3b82f6', dotOutlineColor = '#1E3A8A' }) => {
  const rows = metric ? buildRowsFromMetric(metric) : [];
  const combined = metric?.raw_graph_data ? buildCombinedSeries(metric.raw_graph_data) : null;

  if (compact) {
    const pct = metric?.current_quarter?.growth != null ? `${(metric.current_quarter.growth * 100).toFixed(1)}%` : '—';
    const sparkVals = combined ? combined.map((d) => d.current) : null;
    const isPositive = metric?.current_quarter?.growth != null ? metric.current_quarter.growth >= 0 : null;

    const MiniSpark = ({ values = [], stroke = color }) => {
      if (!values || values.length === 0) return null;
      const w = 40;
      const h = 12;
      const min = Math.min(...values);
      const max = Math.max(...values);
      const range = max - min || 1;
      const points = values.map((v, i) => {
        const x = (i / (values.length - 1 || 1)) * w;
        const y = h - ((v - min) / range) * h;
        return `${x},${y}`;
      });
      return (
        <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} xmlns="http://www.w3.org/2000/svg">
          <polyline
            fill="none"
            stroke={stroke}
            strokeWidth="1.5"
            points={points.join(' ')}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      );
    };

    return (
      <div className="p-3 rounded-lg border border-gray-200 bg-white hover:shadow-md transition-all flex items-center justify-between gap-3 overflow-hidden">
        <div className="flex-1 min-w-0">
          <div className="text-sm font-semibold text-gray-700 truncate">{title}</div>
        </div>
        <div className="flex items-center gap-3">
          <div>
            <MiniSpark values={sparkVals} stroke={color} />
          </div>
          <div className="flex items-center gap-1 text-sm font-semibold">
            {isPositive === true ? (
              <TrendingUp className="w-4 h-4 text-green-600" />
            ) : isPositive === false ? (
              <TrendingDown className="w-4 h-4 text-red-600" />
            ) : null}
            <span>{pct}</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className="p-5 rounded-lg border border-gray-200 bg-white shadow-sm hover:shadow-md transition-all"
      style={{ animation: 'fadeInUp 0.5s ease-out' }}
    >
      <div className="mb-4 pb-4 border-b border-gray-100" style={{ animation: 'fadeInUp 0.5s ease-out' }}>
        <p className="text-lg font-bold text-gray-800">{title}</p>
      </div>

      <div className="grid grid-cols-1 gap-3">
        <div className="space-y-4">
          {rows.map((r, i) => {
            const change = r.growth != null ? (r.growth * 100).toFixed(1) + '%' : '—';
            const isPositive = typeof change === 'string' && !change.startsWith('-') && change !== '—';
            const seriesArr = seriesObjToArray(r.series);

            return (
              <div
                key={i}
                className="metric-row"
                style={{
                  opacity: 0,
                  animation: `fadeInUp 0.5s ease-out ${i * 80}ms forwards`,
                }}
              >
                <div className="flex items-center justify-between pb-3">
                  <div>
                    <div className="text-xs font-medium text-gray-500 uppercase tracking-wide">{r.label}</div>
                    <div className="text-xl font-bold text-gray-900 mt-1">{formatNumber(r.amount)}</div>
                  </div>
                  <div
                    className={`text-sm font-semibold flex items-center gap-1 px-2 py-1 rounded-full ${
                      isPositive ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                    }`}
                  >
                    {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                    {change}
                  </div>
                </div>

                <div style={{ height: 140 }} className="mt-3 relative">
                  {seriesArr ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={seriesArr} margin={{ top: 8, right: 16, left: -20, bottom: 8 }}>
                        <defs>
                          <linearGradient id={`gradient-${title}-${i}`} x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor={color} stopOpacity={0.3} />
                            <stop offset="100%" stopColor={color} stopOpacity={0.02} />
                          </linearGradient>
                        </defs>

                        <CartesianGrid strokeDasharray="4 4" stroke="rgba(0,0,0,0.08)" vertical={true} />
                        <XAxis dataKey="name" tick={{ fontSize: 12 }} tickLine={false} />
                        <YAxis tick={{ fontSize: 12 }} tickLine={false} />

                        <Tooltip
                          content={<FixedTooltipInside />}
                          cursor={{ stroke: color, strokeWidth: 1, strokeDasharray: '4 4' }}
                        />

                        <Line
                          type="monotone"
                          dataKey="value"
                          stroke={color}
                          strokeWidth={2.5}
                          fill={`url(#gradient-${title}-${i})`}
                          dot={{ r: 2, fill: color, stroke: dotOutlineColor, strokeWidth: 3 }}
                          activeDot={{ r: 4, fill: color, stroke: dotOutlineColor, strokeWidth: 3 }}
                          isAnimationActive={true}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  ) : null}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default MetricCard;
