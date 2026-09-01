export function ThinkingTrace({ steps }: { steps: string[] }) {
  const latest = steps.at(-1);
  if (!latest) return null;
  return (
    <div className="rounded-xl border border-[var(--line)] bg-[var(--bg2)] px-3 py-2.5">
      <div className="text-sm text-[var(--txt2)]">{latest}</div>
    </div>
  );
}
