export type TaskItem = { id: string; name: string; status: string };

function isRunning(status: string) {
  return status !== "completed" && status !== "done" && status !== "failed";
}

export function TaskRows({ tasks }: { tasks: TaskItem[] }) {
  const active = tasks.filter((t) => isRunning(t.status));
  if (!active.length) return null;

  return (
    <div className="space-y-2">
      {active.map((t) => (
        <div
          key={t.id}
          className="flex items-center justify-between rounded-lg border border-[var(--line)] bg-[var(--surface)] px-3 py-2"
        >
          <span className="text-sm">{t.name}</span>
          <span className="task-status-running font-mono text-[11px] uppercase tracking-wider text-[var(--accent2)]">
            {t.status}
          </span>
        </div>
      ))}
    </div>
  );
}
