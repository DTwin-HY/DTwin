import { TrendingUp, TrendingDown } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, BarChart, Bar } from 'recharts';

const formatNumber = (num) => {
  if (Math.abs(num) >= 1e6) return `${(num / 1e6).toFixed(1)}M`;
  if (Math.abs(num) >= 1e3) return `${(num / 1e3).toFixed(1)}k`;
  return String(num);
};

const buildRowsFromMetric = (metric) => {
  if (!metric) return [];
  const { current_quarter, previous_quarter, ytd, raw_graph_data } = metric;
  return [
    { label: 'Current quarter', amount: current_quarter?.amount, growth: current_quarter?.growth, series: raw_graph_data?.current_quarter },
    { label: 'Previous quarter', amount: previous_quarter?.amount, growth: previous_quarter?.growth, series: raw_graph_data?.previous_quarter },
    { label: 'YTD', amount: ytd?.amount, growth: ytd?.growth, series: raw_graph_data?.ytd },
  ];
};

const seriesObjToArray = (obj, isCurrentQuarter = false, totalWeeksInQuarter = 13) => {
  if (!obj) return null;
  
const dataArray = Array.isArray(obj)
  ? obj.map((v, i) => ({ week: i, value: +v }))
  : Object.keys(obj).sort((a,b)=>a-b).map(k => ({ week: +k, value: obj[k] }));
  
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
    <div style={{
      position: 'absolute',
      left: coordinate.x + 5,
      top: coordinate.y - 30,
      background: 'rgba(255,255,255,0.9)',
      padding: '2px 6px',
      borderRadius: 4,
      fontSize: 12,
      pointerEvents: 'none',
      border: '1px solid rgba(0,0,0,0.1)',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    }}>
      {formatNumber(payload[0].value)}
    </div>
  );
};

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

const MiniSpark = ({ values = [], stroke }) => {
  if (!values.length) return null;
  const w = 40, h = 12, min = Math.min(...values), max = Math.max(...values), range = max - min || 1;
  const points = values.map((v, i) => `${(i / (values.length - 1 || 1)) * w},${h - ((v - min) / range) * h}`).join(' ');
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <polyline fill="none" stroke={stroke} strokeWidth="1.5" points={points} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
};

export const MetricCard = ({ title, metric = null, compact = false, color = '#3b82f6', dotOutlineColor = '#1E3A8A', currentMonth = new Date().getMonth() }) => {
  if (compact) {
    const combined = Object.values(metric?.raw_graph_data?.current_quarter || {});
    const growth = metric?.current_quarter?.growth;
    const pct = growth != null ? `${(growth * 100).toFixed(1)}%` : '—';
    const isPositive = growth != null ? growth >= 0 : null;
    return (
      <div className="p-3 rounded-lg border border-gray-200 bg-white hover:shadow-md transition-all flex items-center justify-between gap-3 overflow-hidden">
        <div className="flex-1 min-w-0">
          <div className="text-lg font-semibold text-gray-700 truncate">{title}</div>
        </div>
        <div className="flex items-center gap-3">
          <MiniSpark values={combined} stroke={color} />
          <div className={`flex items-center gap-1 text-sm font-semibold ${isPositive ? 'text-green-700' : 'text-red-700'}`}>
            {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            <span>{pct}</span>
          </div>
        </div>
      </div>
    );
  }

  const rows = buildRowsFromMetric(metric);

  return (
    <div className="p-5 rounded-lg border border-gray-200 bg-white shadow-sm hover:shadow-md transition-all">
      <div className="mb-4 pb-4 border-b border-gray-100">
        <p className="text-lg font-bold text-gray-800">{title}</p>
      </div>
      <div className="grid grid-cols-1 gap-3">
        <div className="space-y-4">
          {rows.map((r, i) => {
            const change = r.growth != null ? (r.growth * 100).toFixed(1) + '%' : '—';
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
              <div key={i} style={{ opacity: 0, animation: `fadeInUp 0.5s ease-out ${i * 80}ms forwards` }}>
                <div className="flex items-center justify-between pb-3">
                  <div>
                    <div className="text-xs font-medium text-gray-500 uppercase tracking-wide">{r.label}</div>
                    <div className="text-xl font-bold text-gray-900 mt-1">{formatNumber(r.amount)}</div>
                  </div>
                  <div className={`text-sm font-semibold flex items-center gap-1 px-2 py-1 rounded-full ${isPositive ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                    {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                    {change}
                  </div>
                </div>
                <div style={{ height: 140 }} className="mt-3 relative">
                  {seriesArr && (
                    <ResponsiveContainer width="100%" height={140}>
                      {r.label === 'YTD' ? (
                        <BarChart data={seriesArr} margin={{ top: 5, right: 0, left: -55, bottom: 0 }}>
                          <CartesianGrid strokeDasharray="4 4" stroke="rgba(0,0,0,0.08)" vertical />
                          <XAxis
                            dataKey="week"
                            tick={{ fontSize: 12 }}
                            tickLine={false}
                            ticks={seriesArr.map(d => d.week)}
                            tickFormatter={(week) => {
                              const weeksPerMonth = Math.ceil(seriesArr.length / monthLabels.length);
                              const monthIndex = Math.floor(week / weeksPerMonth);
                              return monthLabels[monthIndex] || '';
                            }}
                          />
                          <YAxis hide={false} tick={false} axisLine={false} tickLine={false} domain={[0, 'auto']} />
                          <Tooltip content={<FixedTooltipInside />} cursor={{ fill: 'rgba(0,0,0,0.05)' }} />
                          <Bar dataKey="value" fill={color} />
                        </BarChart>
                      ) : (
                        <LineChart data={seriesArr} margin={{ top: 30, right: 10, left: -30, bottom: 0 }}>
                          <defs>
                            <linearGradient id={`gradient-${title}-${i}`} x1="0" y1="0" x2="0" y2="1">
                              <stop offset="0%" stopColor={color} stopOpacity={0.3} />
                              <stop offset="100%" stopColor={color} stopOpacity={0.02} />
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="4 4" stroke="rgba(0,0,0,0.08)" vertical />
                          <XAxis 
                            dataKey="week"
                            type="number"
                            domain={[0, isCurrentQuarter ? 12 : 'dataMax']}
                            tick={{ fontSize: 12 }}
                            tickLine={false}
                            ticks={isCurrentQuarter ? [0, 5, 9] : seriesArr.map(d => d.week)} 
                            tickFormatter={(week) => {
                              if (isCurrentQuarter) {
                                switch(week) {
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
                              const weeksPerMonth = Math.ceil(seriesArr.filter(d => d.value !== null).length / monthLabels.length);
                              const monthIndex = Math.floor((week - seriesArr[0].week) / weeksPerMonth);
                              const isFirstWeekOfMonth = (week - seriesArr[0].week) % weeksPerMonth === 0;
                              return isFirstWeekOfMonth ? (monthLabels[monthIndex] || '') : '';
                            }}
                          />
                          <YAxis hide={false} tick={false} axisLine={false} tickLine={false} domain={[0, 'auto']} />
                          <Tooltip content={<FixedTooltipInside />} cursor={{ stroke: color, strokeWidth: 1, strokeDasharray: '4 4' }} />
                          <Line 
                            type="monotone" 
                            dataKey="value" 
                            stroke={color} 
                            strokeWidth={2.5} 
                            fill={`url(#gradient-${title}-${i})`}
                            dot={ false }
                            activeDot={{ r: 4, fill: color, stroke: dotOutlineColor, strokeWidth: 3 }}
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
