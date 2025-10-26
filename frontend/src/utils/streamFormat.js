export const prettifyName = (s = '') =>
  s
    .replace(/_agent$/i, '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());

export const headerLine = (u) => {
  const raw = u.subgraph ?? '';
  const who = prettifyName(raw) || 'AI';

  const kind = u.kind ?? (u.node === 'tools' ? 'tools' : u.node === 'agent' ? 'agent' : 'other');

  if (kind === 'tools') {
    const names = (u.messages ?? [])
      .flatMap((m) => m.tool_calls || [])
      .map((t) => t?.name)
      .filter(Boolean);
    return names.length ? `[${who}] 🔧 ${names.join(', ')}` : `[${who}] 🔧 Tool call`;
  }

  if (kind === 'agent') return `[${who}] → Agent step`;
  if (u.node === 'final' || u.node === 'output') return `[${who}] ✅ Final answer`;

  return `[${who}] ${prettifyName(u.node || '')}`;
};
