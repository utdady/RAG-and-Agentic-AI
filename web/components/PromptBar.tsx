"use client";

import type { FormEvent, ReactNode, RefObject } from "react";

function AttachIcon() {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden
      className="text-[var(--txt2)]"
    >
      <path
        d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export type AttachmentProps = {
  accept: string;
  multiple?: boolean;
  inputRef: RefObject<HTMLInputElement | null>;
  fileNames: string[];
  onFilesChange: () => void;
};

export function PromptBar({
  placeholder,
  busy,
  extra,
  attachment,
  canSubmit,
  onSubmit,
  onStop,
}: {
  placeholder: string;
  busy?: boolean;
  extra?: ReactNode;
  attachment?: AttachmentProps;
  canSubmit?: (value: string) => boolean;
  onSubmit: (value: string) => void;
  onStop?: () => void;
}) {
  function handle(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (busy) return;
    const form = e.currentTarget;
    const input = form.elements.namedItem("q") as HTMLInputElement | null;
    if (!input) return;
    const value = input.value.trim();
    const allowed = canSubmit ? canSubmit(value) : value.length > 0;
    if (!allowed) return;
    onSubmit(value);
    input.value = "";
  }

  return (
    <form onSubmit={handle} className="space-y-2">
      {extra}
      <div className="flex gap-2 rounded-2xl border border-[var(--line)] bg-[var(--surface)] p-2 focus-within:border-accent">
        {attachment ? (
          <>
            <input
              ref={attachment.inputRef}
              type="file"
              accept={attachment.accept}
              multiple={attachment.multiple}
              onChange={attachment.onFilesChange}
              className="hidden"
            />
            <button
              type="button"
              disabled={busy}
              onClick={() => attachment.inputRef.current?.click()}
              aria-label="Attach file"
              className="shrink-0 rounded-xl p-2 hover:bg-[var(--bg)] disabled:opacity-60"
            >
              <AttachIcon />
            </button>
          </>
        ) : null}
        <input
          name="q"
          disabled={busy}
          placeholder={placeholder}
          className="min-w-0 flex-1 bg-transparent px-1 py-2 text-sm outline-none placeholder:text-[var(--txt2)] disabled:opacity-60"
        />
        {busy ? (
          <button
            type="button"
            onClick={onStop}
            className="rounded-xl border border-[var(--warn)]/50 bg-[var(--warn)]/15 px-4 py-2 text-sm font-medium text-[var(--warn)] hover:bg-[var(--warn)]/25"
          >
            Stop
          </button>
        ) : (
          <button
            type="submit"
            className="rounded-xl bg-accent px-4 py-2 text-sm font-medium text-[#07090f]"
          >
            Run
          </button>
        )}
      </div>
      {attachment && attachment.fileNames.length ? (
        <p className="truncate px-1 text-xs text-[var(--txt2)]">
          {attachment.fileNames.join(", ")}
        </p>
      ) : null}
    </form>
  );
}
