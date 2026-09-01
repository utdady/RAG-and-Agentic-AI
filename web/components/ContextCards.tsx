export type ContextItem = { title: string; snippet: string; source?: string };

export function ContextCards({ items }: { items: ContextItem[] }) {
  if (!items.length) return null;
  return (
    <div className="grid gap-2">
      <div className="font-mono text-[11px] tracking-widest uppercase text-[var(--txt2)]">
        Context {items.length}
      </div>
      {items.map((c, i) => (
        <article
          key={`${c.title}-${i}`}
          className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-3"
        >
          <h4 className="text-sm font-medium">{c.title}</h4>
          <p className="mt-1 text-sm text-[var(--txt2)]">{c.snippet}</p>
          {c.source ? (
            <p className="mt-2 font-mono text-[11px] text-accent">{c.source}</p>
          ) : null}
        </article>
      ))}
    </div>
  );
}
