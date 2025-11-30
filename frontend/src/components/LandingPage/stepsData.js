export const STEPS = [
  {
    id: 'supervisor',
    title: 'Supervisor coordinates everything',
    body: 'Built on LangGraph, the Supervisor agent routes every request through the graph, decides which agents to wake up in which order and makes sure result matches the request.',
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
    id: 'whatif',
    title: 'What-if simulations without touching real data',
    body: 'Spin up scenario agents that fork the graph state and answer “what if” questions. The Supervisor keeps these sandboxes isolated from your real customers and orders.',
    nodeId: 'whatif',
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
    id: 'whatif',
    nodeId: 'whatif',
    caption: 'What-If Scenario agent combines margin and demand shift to estimate future revenue.',
  },
];
