import { motion } from 'framer-motion';

const Graph = ({ activeNodeId }) => {
  const nodes = [
    { id: 'supervisor', label: 'Supervisor', x: 52, y: 20 },
    { id: 'mcp', label: 'MCP', x: 20, y: 28 },
    { id: 'whatif', label: 'What-If', x: 82, y: 25 },

    { id: 'sales-agent', label: 'Sales Agent', x: 34, y: 52 },
    { id: 'sales-tool', label: 'Sales Tool', x: 20, y: 74 },

    { id: 'storage-agent', label: 'Storage Agent', x: 69, y: 52 },

    { id: 'data', label: 'Database', x: 82, y: 75 },

    { id: 'sql-agent', label: 'SQL Agent', x: 52, y: 86 },
  ];

  const edges = [
    { source: 'supervisor', target: 'sales-agent' },
    { source: 'supervisor', target: 'storage-agent' },
    { source: 'supervisor', target: 'mcp' },
    { source: 'supervisor', target: 'whatif' },
    { source: 'sales-agent', target: 'sales-tool' },
    { source: 'sql-agent', target: 'sales-agent' },
    { source: 'sql-agent', target: 'storage-agent' },
    { source: 'sql-agent', target: 'data' },
  ];

  const newAgentNodes = [
    { id: 'ghost-top-left', x: 10, y: 18, label: 'New agent' },
    { id: 'ghost-right', x: 92, y: 46, label: 'New agent' },
    { id: 'ghost-bottom-left', x: 15, y: 88, label: 'New agent' },
  ];

  return (
    <div className="relative h-full w-full rounded-3xl border border-slate-800">
      {/* Edges */}
      <svg className="h-full w-full">
        {edges.map((edge) => {
          const from = nodes.find((n) => n.id === edge.source);
          const to = nodes.find((n) => n.id === edge.target);
          if (!from || !to) return null;

          return (
            <line
              key={`${edge.source}-${edge.target}-base`}
              x1={`${from.x}%`}
              y1={`${from.y}%`}
              x2={`${to.x}%`}
              y2={`${to.y}%`}
              stroke="rgba(148,163,184,0.35)"
              strokeWidth={2}
            />
          );
        })}
      </svg>

      {/* Highlighted edges */}
      <svg className="pointer-events-none absolute inset-0 h-full w-full">
        {edges.map((edge) => {
          const from = nodes.find((n) => n.id === edge.source);
          const to = nodes.find((n) => n.id === edge.target);
          if (!from || !to) return null;

          const isHighlighted = from.id === activeNodeId || to.id === activeNodeId;

          if (!isHighlighted) return null;

          return (
            <line
              key={`${edge.source}-${edge.target}`}
              x1={`${from.x}%`}
              y1={`${from.y}%`}
              x2={`${to.x}%`}
              y2={`${to.y}%`}
              stroke="rgba(56,189,248,0.9)"
              strokeWidth={2.5}
            />
          );
        })}
      </svg>

      {/* Nodes */}
      {nodes.map((node) => {
        const isActive = node.id === activeNodeId;
        const isSupervisor = node.id === 'supervisor';
        const isAgent = ['sales-agent', 'storage-agent', 'sql-agent'].includes(node.id);

        const baseSize = isSupervisor
          ? 'h-20 w-20 md:h-24 md:w-24'
          : isAgent
            ? 'h-18 w-18 md:h-20 md:w-20'
            : 'h-14 w-14 md:h-16 md:w-16';

        let bgClasses = 'border-slate-600 bg-slate-900/90 text-slate-100';
        if (isSupervisor || isActive) {
          bgClasses = 'bg-indigo-600/90 border-indigo-200 text-white';
        }

        return (
          <motion.div
            key={node.id}
            className={[
              'absolute flex -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border text-[10px] font-medium',
              baseSize,
              bgClasses,
            ].join(' ')}
            style={{ left: `${node.x}%`, top: `${node.y}%` }}
            animate={{
              scale: isSupervisor
                ? isActive
                  ? 1.28
                  : 1.18
                : isAgent
                  ? isActive
                    ? 1.2
                    : 1.05
                  : isActive
                    ? 1.12
                    : 1,
              boxShadow:
                isSupervisor || isActive ? '0 0 40px rgba(129,140,248,0.7)' : '0 0 0 rgba(0,0,0,0)',
            }}
            transition={{ type: 'spring', stiffness: 260, damping: 20 }}
          >
            {node.label}
          </motion.div>
        );
      })}

      {/* New/ghost nodes) */}
      {newAgentNodes.map((node) => (
        <motion.div
          key={node.id}
          className="absolute flex h-12 -translate-x-1/2 -translate-y-1/2 flex-col items-center justify-center rounded-full border bg-slate-900/60 text-[9px] font-medium md:h-14 md:w-14"
          style={{ left: `${node.x}%`, top: `${node.y}%` }}
          animate={{
            opacity: [0.35, 0.9, 0.35],
            scale: [1, 1.08, 1],
          }}
          transition={{ duration: 2.8, repeat: Infinity, ease: 'easeInOut' }}
        >
          <span className="text-base leading-none">+</span>
          <span className="mt-0.5">New agent</span>
        </motion.div>
      ))}
    </div>
  );
};

export default Graph;
