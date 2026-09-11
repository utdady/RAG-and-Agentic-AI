"use client";

import { useState } from "react";

function CopyIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden>
      <rect
        x="9"
        y="9"
        width="11"
        height="11"
        rx="2"
        stroke="currentColor"
        strokeWidth="1.75"
      />
      <path
        d="M5 15V5a2 2 0 012-2h10"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
      />
    </svg>
  );
}

function EditIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M12 20h9"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
      />
      <path
        d="M16.5 3.5a2.12 2.12 0 013 3L7 19l-4 1 1-4L16.5 3.5z"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M5 13l4 4L19 7"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function MessageActions({
  align = "start",
  copyText,
  onEdit,
  disabled,
}: {
  align?: "start" | "end";
  copyText?: string;
  onEdit?: () => void;
  disabled?: boolean;
}) {
  const [copied, setCopied] = useState(false);
  const canCopy = Boolean(copyText?.trim());
  if (!canCopy && !onEdit) return null;

  async function handleCopy() {
    if (!copyText?.trim() || disabled) return;
    try {
      await navigator.clipboard.writeText(copyText);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      /* ignore clipboard failures */
    }
  }

  return (
    <div
      className={`flex items-center gap-0.5 ${
        align === "end" ? "justify-end" : "justify-start"
      }`}
    >
      {canCopy ? (
        <button
          type="button"
          disabled={disabled}
          onClick={() => {
            void handleCopy();
          }}
          aria-label={copied ? "Copied" : "Copy message"}
          title={copied ? "Copied" : "Copy"}
          className="rounded-lg p-1.5 text-[var(--txt3)] transition hover:bg-[var(--surface)] hover:text-[var(--txt2)] disabled:opacity-40"
        >
          {copied ? <CheckIcon /> : <CopyIcon />}
        </button>
      ) : null}
      {onEdit ? (
        <button
          type="button"
          disabled={disabled}
          onClick={onEdit}
          aria-label="Edit message"
          title="Edit"
          className="rounded-lg p-1.5 text-[var(--txt3)] transition hover:bg-[var(--surface)] hover:text-[var(--txt2)] disabled:opacity-40"
        >
          <EditIcon />
        </button>
      ) : null}
    </div>
  );
}
