import { TrendingUp, TrendingDown } from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar,
} from 'recharts';

const formatNumber = (num) => {
  if (Math.abs(num) >= 1e6) return `${(num / 1e6).toFixed(1)}M`;
  if (Math.abs(num) >= 1e3) return `${(num / 1e3).toFixed(1)}k`;
  return String(num);
};

const buildRowsFromMetric = (metric) => {
  if (!metric) return [];
  const { current_quarter, previous_quarter, ytd, raw_graph_data } = metric;
  return [
    {
      label: 'Current quarter',
      amount: current_quarter?.amount,
      growth: current_quarter?.growth,
      series: raw_graph_data?.current_quarter,
    },
    {
      label: 'Previous quarter',
      amount: previous_quarter?.amount,
      growth: previous_quarter?.growth,
      series: raw_graph_data?.previous_quarter,
    },
    { label: 'YTD', amount: ytd?.amount, growth: ytd?.growth, series: raw_graph_data?.ytd },
  ];
};

const seriesObjToArray = (obj, isCurrentQuarter = false, totalWeeksInQuarter = 13) => {
  if (!obj) return null;

  const dataArray = Array.isArray(obj)
    ? obj.map((v, i) => ({ week: i, value: +v }))
    : Object.keys(obj)
        .sort((a, b) => a - b)
        .map((k) => ({ week: +k, value: obj[k] }));

  if (isCurrentQuarter && dataArray.length < totalWeeksInQuarter) {
    const lastWeek = dataArray[dataArray.length - 1].week;
    for (let i = dataArray.length; i < totalWeeksInQuarter; i++) {
      dataArray.push({ week: lastWeek + (i - dataArray.length + 1), value: null });
    }
  }

  return dataArray;
};

const FixedTooltipInside = ({ active, payload, coordinate }) => {
  if (!active || !payload?.[0] || !coordinate) return null;
  return (
    <div
      style={{
        position: 'absolute',
        left: coordinate.x + 5,
        top: coordinate.y - 30,
        background: 'hsl(var(--background))',
        padding: '4px 8px',
        borderRadius: 6,
        fontSize: 12,
        pointerEvents: 'none',
        border: '1px solid rgba(148,163,184,0.5)', // slate-400-ish
        boxShadow: '0 6px 18px rgba(15,23,42,0.6)', // dark glow
        color: 'hsl(var(--foreground))',
        whiteSpace: 'nowrap',
      }}
    >
      {formatNumber(payload[0].value)}
    </div>
  );
};

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

const MiniSpark = ({ values = [], stroke }) => {
  if (!values.length) return null;
  const w = 40,
    h = 12,
    min = Math.min(...values),
    max = Math.max(...values),
    range = max - min || 1;
  const points = values
    .map((v, i) => `${(i / (values.length - 1 || 1)) * w},${h - ((v - min) / range) * h}`)
    .join(' ');
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <polyline
        fill="none"
        stroke={stroke}
        strokeWidth="1.5"
        points={points}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};

export const MetricCard = ({
  title,
  metric = null,
  compact = false,
  color = '#3b82f6',
  dotOutlineColor = '#1E3A8A',
  currentMonth = new Date().getMonth(),
}) => {
  console.log('MetricCard render:', title, 'compact =', compact); // <--- add this

  if (compact) {
    const combined = Object.values(metric?.raw_graph_data?.current_quarter || {});
    const growth = metric?.current_quarter?.growth;
    const pct = growth !== null ? `${(growth * 100).toFixed(1)}%` : '—';
    const isPositive = growth !== null ? growth >= 0 : null;
    return (
      <div
        className="flex items-center justify-between gap-3 overflow-hidden rounded-xl border p-3 transition-all hover:shadow-lg"
        style={{ borderColor: '#e5e7eb', backgroundColor: '#ffffff' }}
      >
        <div className="min-w-0 flex-1">
          <div className="truncate text-sm font-semibold md:text-base" style={{ color: '#1f2937' }}>
            {title}
          </div>
        </div>
        <div className="flex items-center gap-3">
          <MiniSpark values={combined} stroke={color} />
          <div
            className={`flex items-center gap-1 rounded-full px-2 py-1 text-xs font-semibold md:text-sm ${
              isPositive
                ? 'bg-emerald-500/10 text-emerald-600'
                : isPositive === false
                  ? 'bg-rose-500/10 text-rose-600'
                  : 'bg-gray-100 text-gray-600'
            }`}
          >
            {isPositive ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
            <span>{pct}</span>
          </div>
        </div>
      </div>
    );
  }

  const rows = buildRowsFromMetric(metric);

  return (
    <div
      className="rounded-2xl border p-5 shadow-lg transition-all"
      style={{ borderColor: '#e5e7eb', backgroundColor: '#ffffff' }}
    >
      <div className="mb-4 border-b pb-4" style={{ borderColor: '#e5e7eb' }}>
        <p className="text-lg font-bold md:text-xl" style={{ color: '#1f2937' }}>
          {title}
        </p>
      </div>
      <div className="grid grid-cols-1 gap-3">
        <div className="space-y-4">
          {rows.map((r, i) => {
            const change = r.growth !== null ? (r.growth * 100).toFixed(1) + '%' : '—';
            const isPositive = change !== '—' && !change.startsWith('-');

            let monthLabels = [];
            let isCurrentQuarter = false;

            if (r.label === 'Current quarter') {
              const quarterStart = currentMonth - (currentMonth % 3);
              monthLabels = MONTHS.slice(quarterStart, quarterStart + 3);
              isCurrentQuarter = true;
            } else if (r.label === 'Previous quarter') {
              const prevQuarterStart = currentMonth - (currentMonth % 3) - 3;
              monthLabels = MONTHS.slice(prevQuarterStart, prevQuarterStart + 3);
            } else if (r.label === 'YTD') {
              monthLabels = MONTHS.slice(0, currentMonth + 1);
            }

            const seriesArr = seriesObjToArray(r.series, isCurrentQuarter, 13);

            return (
              <div
                key={i}
                style={{ opacity: 0, animation: `fadeInUp 0.5s ease-out ${i * 80}ms forwards` }}
              >
                <div className="flex items-center justify-between pb-3">
                  <div>
                    <div
                      className="text-[13px] font-medium tracking-wide uppercase"
                      style={{ color: '#6b7280' }}
                    >
                      {r.label}
                    </div>
                    <div className="mt-1 text-xl font-bold" style={{ color: '#1f2937' }}>
                      {formatNumber(r.amount)}
                    </div>
                  </div>
                  <div
                    className={`flex items-center gap-1 rounded-full px-2 py-1 text-xs font-semibold md:text-sm ${
                      isPositive
                        ? 'bg-emerald-500/10 text-emerald-600'
                        : 'bg-rose-500/10 text-rose-600'
                    }`}
                  >
                    {isPositive ? (
                      <TrendingUp className="h-4 w-4" />
                    ) : (
                      <TrendingDown className="h-4 w-4" />
                    )}
                    {change}
                  </div>
                </div>
                <div style={{ height: 140 }} className="relative mt-3">
                  {seriesArr && (
                    <ResponsiveContainer width="100%" height={140}>
                      {r.label === 'YTD' ? (
                        <BarChart
                          data={seriesArr}
                          margin={{ top: 5, right: 0, left: -55, bottom: 0 }}
                        >
                          <CartesianGrid
                            strokeDasharray="4 4"
                            stroke="rgba(209,213,219,0.5)"
                            vertical
                          />
                          <XAxis
                            dataKey="week"
                            tick={{ fontSize: 13, fill: '#1f2937' }}
                            tickLine={false}
                            ticks={seriesArr.map((d) => d.week)}
                            tickFormatter={(week) => {
                              const weeksPerMonth = Math.ceil(
                                seriesArr.length / monthLabels.length,
                              );
                              const monthIndex = Math.floor(week / weeksPerMonth);
                              return monthLabels[monthIndex] || '';
                            }}
                          />
                          <YAxis
                            hide={false}
                            tick={false}
                            axisLine={false}
                            tickLine={false}
                            domain={[0, 'auto']}
                          />
                          <Tooltip
                            content={<FixedTooltipInside />}
                            cursor={{ fill: 'rgba(148,163,184,0.12)' }}
                          />
                          <Bar dataKey="value" fill={color} radius={[4, 4, 0, 0]} />
                        </BarChart>
                      ) : (
                        <LineChart
                          data={seriesArr}
                          margin={{ top: 30, right: 10, left: -45, bottom: 0 }}
                        >
                          <defs>
                            <linearGradient
                              id={`gradient-${title}-${i}`}
                              x1="0"
                              y1="0"
                              x2="0"
                              y2="1"
                            >
                              <stop offset="0%" stopColor={color} stopOpacity={0.45} />
                              <stop offset="100%" stopColor={color} stopOpacity={0.02} />
                            </linearGradient>
                          </defs>
                          <CartesianGrid
                            strokeDasharray="4 4"
                            stroke="rgba(148,163,184,0.25)"
                            vertical
                          />
                          <XAxis
                            dataKey="week"
                            type="number"
                            domain={[0, isCurrentQuarter ? 12 : 'dataMax']}
                            tick={{
                              fontSize: 13,
                              fill: '#1f2937',
                            }}
                            tickLine={false}
                            ticks={isCurrentQuarter ? [0, 5, 9] : seriesArr.map((d) => d.week)}
                            tickFormatter={(week) => {
                              if (isCurrentQuarter) {
                                switch (week) {
                                  case 0:
                                    return monthLabels[0] || '';
                                  case 5:
                                    return monthLabels[1] || '';
                                  case 9:
                                    return monthLabels[2] || '';
                                  default:
                                    return '';
                                }
                              }
                              const weeksPerMonth = Math.ceil(
                                seriesArr.filter((d) => d.value !== null).length /
                                  monthLabels.length,
                              );
                              const monthIndex = Math.floor(
                                (week - seriesArr[0].week) / weeksPerMonth,
                              );
                              const isFirstWeekOfMonth =
                                (week - seriesArr[0].week) % weeksPerMonth === 0;
                              return isFirstWeekOfMonth ? monthLabels[monthIndex] || '' : '';
                            }}
                          />
                          <YAxis
                            hide={false}
                            tick={false}
                            axisLine={false}
                            tickLine={false}
                            domain={[0, 'auto']}
                          />
                          <Tooltip
                            content={<FixedTooltipInside />}
                            cursor={{
                              stroke: color,
                              strokeWidth: 1,
                              strokeDasharray: '4 4',
                            }}
                          />
                          <Line
                            type="monotone"
                            dataKey="value"
                            stroke={color}
                            strokeWidth={5}
                            fill={`url(#gradient-${title}-${i})`}
                            dot={false}
                            activeDot={{
                              r: 4,
                              fill: color,
                              stroke: dotOutlineColor,
                              strokeWidth: 3,
                            }}
                            connectNulls={false}
                            isAnimationActive
                          />
                        </LineChart>
                      )}
                    </ResponsiveContainer>
                  )}
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
