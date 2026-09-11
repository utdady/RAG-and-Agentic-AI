"use client";

type GuideTable = { name: string; columns: string[] };

export function DatasetGuide({
  blurb,
  tables,
  starters,
  busy,
  onStarter,
}: {
  blurb: string;
  tables: GuideTable[];
  starters: string[];
  busy?: boolean;
  onStarter: (prompt: string) => void;
}) {
  return (
    <div className="max-w-2xl space-y-3 rounded-[10px] border border-[var(--line)] bg-[var(--bg2)] px-4 py-3.5">
      <div>
        <p className="mb-1 font-mono text-[11px] uppercase tracking-wider text-accent">
          Dataset
        </p>
        <p className="text-sm leading-relaxed text-[var(--txt2)]">{blurb}</p>
      </div>

      <details className="rounded-lg border border-[var(--line)] bg-[var(--surface)]">
        <summary className="cursor-pointer list-none px-3 py-2 font-mono text-[12px] text-[var(--txt)] [&::-webkit-details-marker]:hidden">
          Explore schema
          <span className="ml-2 text-[var(--txt3)]">
            {tables.length} tables
          </span>
        </summary>
        <ul className="space-y-2.5 border-t border-[var(--line)] px-3 py-3">
          {tables.map((table) => (
            <li key={table.name}>
              <p className="font-mono text-[12.5px] text-accent">{table.name}</p>
              <p className="mt-0.5 font-mono text-[11px] leading-relaxed text-[var(--txt3)]">
                {table.columns.join(" · ")}
              </p>
            </li>
          ))}
        </ul>
      </details>

      {starters.length ? (
        <div>
          <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-[var(--txt3)]">
            Try asking
          </p>
          <div className="flex flex-wrap gap-2">
            {starters.map((prompt) => (
              <button
                key={prompt}
                type="button"
                disabled={busy}
                onClick={() => onStarter(prompt)}
                className="rounded-full border border-[var(--line-hover)] bg-[var(--surface)] px-3 py-1.5 text-left text-[12.5px] text-[var(--txt2)] transition hover:border-accent hover:text-accent disabled:cursor-not-allowed disabled:opacity-50"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
