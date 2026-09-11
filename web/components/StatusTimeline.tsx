"use client";

import { useState } from "react";

export type StatusStep = {
  key: string;
  kind: "status" | "thinking" | "task" | "tool";
  label: string;
  status: "running" | "done" | "failed";
};

function kindLabel(kind: StatusStep["kind"]) {
  switch (kind) {
    case "tool":
      return "Tool";
    case "task":
      return "Step";
    case "thinking":
      return "Working";
    default:
      return "Status";
  }
}

function statusTone(status: StatusStep["status"]) {
  if (status === "failed") return "text-[var(--warn)]";
  if (status === "done") return "text-[var(--txt3)]";
  return "text-accent";
}

function GridIcon({ active }: { active?: boolean }) {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 16 16"
      fill="currentColor"
      aria-hidden
      className={`shrink-0 ${active ? "text-accent" : "text-[var(--txt3)]"}`}
    >
      <rect x="1" y="1" width="5" height="5" rx="1" />
      <rect x="10" y="1" width="5" height="5" rx="1" />
      <rect x="1" y="10" width="5" height="5" rx="1" />
      <rect x="10" y="10" width="5" height="5" rx="1" />
    </svg>
  );
}

function ChevronIcon({ open }: { open: boolean }) {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 16 16"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
      className={`shrink-0 text-[var(--txt3)] transition-transform duration-200 ${
        open ? "rotate-180" : "rotate-0"
      }`}
    >
      <path d="M4 6l4 4 4-4" />
    </svg>
  );
}

function StatusGlyph({ status }: { status: StatusStep["status"] }) {
  if (status === "failed") {
    return (
      <span
        className="mt-1.5 inline-block h-1.5 w-1.5 shrink-0 rounded-full bg-[var(--warn)]"
        aria-hidden
      />
    );
  }
  if (status === "done") {
    return (
      <span
        className="mt-1.5 inline-block h-1.5 w-1.5 shrink-0 rounded-full bg-[var(--live)]"
        aria-hidden
      />
    );
  }
  return (
    <span
      className="mt-1.5 inline-block h-1.5 w-1.5 shrink-0 rounded-full bg-accent shadow-[0_0_8px_var(--accent)] task-status-running"
      aria-hidden
    />
  );
}

export function StatusTimeline({
  steps,
  busy,
  elapsed,
}: {
  steps: StatusStep[];
  busy: boolean;
  elapsed?: string;
}) {
  const [open, setOpen] = useState(false);

  if (!steps.length && !busy) return null;

  const liveLabel =
    steps.find((s) => s.status === "running")?.label ||
    (busy ? "Working…" : "");

  const subtitle = busy
    ? liveLabel || "Starting…"
    : steps.length
      ? `${steps.length} step${steps.length === 1 ? "" : "s"}`
      : "Starting…";

  return (
    <details
      open={open}
      onToggle={(e) => setOpen((e.target as HTMLDetailsElement).open)}
      className="w-full rounded-[10px] border border-[var(--line)] bg-[var(--bg2)]"
    >
      <summary className="flex cursor-pointer list-none items-center justify-between gap-3 px-3.5 py-2.5 [&::-webkit-details-marker]:hidden">
        <div className="flex min-w-0 items-center gap-2.5">
          <GridIcon active={busy} />
          <div className="min-w-0">
            <p className="truncate font-mono text-[12.5px] text-[var(--txt)]">
              Process
            </p>
            <p className="truncate font-mono text-[11px] text-[var(--txt3)]">
              {subtitle}
              {elapsed ? ` · ${elapsed}` : ""}
            </p>
          </div>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <span className="font-mono text-[11px] text-[var(--txt3)]">
            {busy ? "live" : "done"}
          </span>
          <ChevronIcon open={open} />
        </div>
      </summary>

      <ol className="space-y-2 border-t border-[var(--line)] px-3.5 py-3">
        {steps.length === 0 && busy ? (
          <li className="flex gap-2.5 text-sm text-[var(--txt2)]">
            <StatusGlyph status="running" />
            <span>Connecting to the demo…</span>
          </li>
        ) : null}
        {steps.map((step) => (
          <li key={step.key} className="flex gap-2.5">
            <StatusGlyph status={step.status} />
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-0.5">
                <p className="text-sm text-[var(--txt)]">{step.label}</p>
                <span
                  className={`font-mono text-[10.5px] uppercase tracking-wider ${statusTone(step.status)}`}
                >
                  {step.status === "running"
                    ? kindLabel(step.kind)
                    : step.status}
                </span>
              </div>
            </div>
          </li>
        ))}
      </ol>
    </details>
  );
}

export function appendThinkingStep(
  steps: StatusStep[],
  label: string,
): StatusStep[] {
  const trimmed = label.trim();
  if (!trimmed) return steps;
  const last = steps.at(-1);
  if (last?.kind === "thinking" && last.label === trimmed) return steps;
  const next: StatusStep[] = [
    ...steps,
    {
      key: `thinking-${steps.length}-${trimmed.slice(0, 24)}`,
      kind: "thinking",
      label: trimmed,
      status: "running",
    },
  ];
  return next.map((s, i) =>
    s.kind === "thinking" && i < next.length - 1 && s.status === "running"
      ? { ...s, status: "done" as const }
      : s,
  );
}

export function upsertTaskStep(
  steps: StatusStep[],
  id: string,
  name: string,
  rawStatus?: string,
): StatusStep[] {
  const status = normalizeStatus(rawStatus);
  const key = `task-${id}`;
  const existing = steps.find((s) => s.key === key);
  if (!existing) {
    return [...steps, { key, kind: "task", label: name, status }];
  }
  return steps.map((s) =>
    s.key === key ? { ...s, label: name || s.label, status } : s,
  );
}

export function upsertToolStep(
  steps: StatusStep[],
  name: string,
  rawStatus?: string,
): StatusStep[] {
  const status = normalizeStatus(rawStatus);
  const key = `tool-${name}`;
  const existing = steps.find((s) => s.key === key);
  if (!existing) {
    return [...steps, { key, kind: "tool", label: name, status }];
  }
  return steps.map((s) => (s.key === key ? { ...s, status } : s));
}

export function finalizeStatusSteps(steps: StatusStep[]): StatusStep[] {
  return steps.map((s) =>
    s.status === "running" ? { ...s, status: "done" as const } : s,
  );
}

function normalizeStatus(raw?: string): StatusStep["status"] {
  const s = (raw || "running").toLowerCase();
  if (s === "failed" || s === "error") return "failed";
  if (
    s === "done" ||
    s === "completed" ||
    s === "complete" ||
    s === "success" ||
    s === "succeeded"
  ) {
    return "done";
  }
  return "running";
}
