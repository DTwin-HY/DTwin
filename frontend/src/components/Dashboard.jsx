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