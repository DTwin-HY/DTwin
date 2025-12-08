export const STEPS = [
  {
    id: 'supervisor',
    title: 'Supervisor coordinates everything',
    body: 'Powered by LangGraph, the Supervisor agent acts as the central brain. It intelligently routes requests through the graph, activates specialized agents in order and ensures every output aligns perfectly matches the request.',
    nodeId: 'supervisor',
  },
  {
    id: 'sales-agent',
    title: 'Sales & Storage agents react to changes',
    body: 'Sales Agent and Storage Agent keep your demand and stock in sync, reacting to new orders and inventory updates.',
    nodeId: 'sales-agent',
  },
  {
    id: 'sql-agent',
    title: 'SQL Agent keeps the twin aligned with your database',
    body: 'The SQL Agent talks to your database. It analyzes table structures and writes queries to fetch data that is needed.',
    nodeId: 'sql-agent',
  },
  {
    id: 'analytics-agent',
    title: 'Analytics Agent runs simulations',
    body: 'Spin up scenario agents that fork the graph state to answer “what if” questions. Perform price sensitivity analysis, inventory forecasting, and revenue projections without impacting your real data.',
    nodeId: 'analytics-agent',
  },
];

export const SCENARIO_STEPS = [
  {
    id: 'prompt',
    nodeId: 'supervisor',
    caption: '“If I raise this product’s price by 10%, how much revenue do we make?”',
  },
  {
    id: 'supervisor',
    nodeId: 'supervisor',
    caption:
      'Supervisor receives the pricing question and decides which agents need to be involved.',
  },
  {
    id: 'sql',
    nodeId: 'sql-agent',
    caption:
      'SQL Agent analyzes the database and writes queries to fetch only data that is needed.',
  },
  {
    id: 'sales',
    nodeId: 'sales-agent',
    caption: 'Sales Agent provides a raport of past sales data for what-if agent to use.',
  },
  {
    id: 'analytics',
    nodeId: 'analytics-agent',
    caption: 'Analytics Agent combines margin and demand shift to estimate future revenue.',
  },
];
