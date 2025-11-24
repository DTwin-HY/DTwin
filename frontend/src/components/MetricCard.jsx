import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, Tooltip, Area, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';

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
  // collect keys from available series and sort
  const idxs = Array.from(new Set(Object.keys(raw_graph_data?.current_quarter || {}).concat(Object.keys(raw_graph_data?.previous_quarter || {})).concat(Object.keys(raw_graph_data?.ytd || {})))).sort((a,b)=>Number(a)-Number(b));
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

export const MetricCard = ({ title, metric = null, compact = false, color = '#3b82f6' }) => {
  const rows = metric ? buildRowsFromMetric(metric) : [];
  const combined = metric?.raw_graph_data ? buildCombinedSeries(metric.raw_graph_data) : null;

  if (compact) {
    // compact: show title, small sparkline and a single percent (use current_quarter.growth)
    const pct = metric?.current_quarter?.growth != null ? `${(metric.current_quarter.growth*100).toFixed(1)}%` : '—';
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
          <polyline fill="none" stroke={stroke} strokeWidth="1.5" points={points.join(' ')} strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    };

    return (
      <div className="p-2 rounded-lg border bg-card/40 border-border/50 transition-colors flex items-center justify-between gap-2 overflow-hidden">
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium truncate">{title}</div>
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

  // full mode: show rows on top and a larger combined chart under them
  return (
    <div className="p-4 rounded-lg border bg-card/40 border-border/50 transition-colors">
      <div className="mb-3">
        <p className="text-sm text-muted-foreground">{title}</p>
      </div>

      <div className="grid grid-cols-1 gap-3">
        <div className="space-y-4">
          {rows.map((r, i) => {
            const change = r.growth != null ? (r.growth * 100).toFixed(1) + '%' : '—';
            const isPositive = typeof change === 'string' && change.startsWith('-') === false && change !== '—';
            const seriesArr = seriesObjToArray(r.series);
            return (
              <div key={i}>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm text-muted-foreground">{r.label}</div>
                    <div className="text-lg font-semibold">{formatNumber(r.amount)}</div>
                  </div>
                  <div className={`text-sm font-medium ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                    {isPositive ? <TrendingUp className="inline-block mr-1 w-4 h-4 text-green-600" /> : <TrendingDown className="inline-block mr-1 w-4 h-4 text-red-600" />}
                    {change}
                  </div>
                </div>

                <div style={{ height: 96 }} className="mt-2">
                  {seriesArr ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={seriesArr} margin={{ top: 6, right: 12, left: 0, bottom: 6 }}>
                        <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.06} />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip formatter={(value) => [value, '']} />
                        <Line type="monotone" dataKey="value" stroke={color} strokeWidth={2} dot={{ r: 2 }} />
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
