export type ToolItem = { name: string; status?: string };

export function ToolChips({ tools }: { tools: ToolItem[] }) {
  if (!tools.length) return null;
  return (
    <div className="flex flex-wrap gap-2">
      {tools.map((t, i) => (
        <span
          key={`${t.name}-${i}`}
          className="rounded-full border border-[var(--line)] bg-[var(--bg2)] px-3 py-1 font-mono text-xs text-accent"
        >
          {t.name}
          {t.status ? ` · ${t.status}` : ""}
        </span>
      ))}
    </div>
  );
}
