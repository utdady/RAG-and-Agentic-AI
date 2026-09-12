"use client";

import {
  useEffect,
  useRef,
  useState,
  type ClipboardEvent,
  type FormEvent,
  type ReactNode,
  type RefObject,
} from "react";

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

function FileTypeIcon({ ext }: { ext: string }) {
  const label = ext.toUpperCase().slice(0, 4) || "FILE";
  const isPdf = ext === "pdf";
  return (
    <span
      className={`flex h-9 w-9 shrink-0 flex-col items-center justify-center rounded-md text-[9px] font-bold leading-none tracking-wide ${
        isPdf
          ? "bg-[#e84a4a] text-white"
          : "bg-[var(--bg)] text-[var(--txt2)] ring-1 ring-[var(--line)]"
      }`}
      aria-hidden
    >
      <svg
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="none"
        className="mb-0.5"
      >
        <path
          d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"
          stroke="currentColor"
          strokeWidth="1.75"
          strokeLinejoin="round"
        />
        <path
          d="M14 2v6h6"
          stroke="currentColor"
          strokeWidth="1.75"
          strokeLinejoin="round"
        />
      </svg>
      {label}
    </span>
  );
}

function CloseIcon() {
  return (
    <svg
      width="12"
      height="12"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.25"
      strokeLinecap="round"
      aria-hidden
    >
      <path d="M18 6L6 18M6 6l12 12" />
    </svg>
  );
}

function fileExt(name: string) {
  const i = name.lastIndexOf(".");
  if (i < 0) return "";
  return name.slice(i + 1).toLowerCase();
}

function displayType(ext: string) {
  if (!ext) return "File";
  return ext.toUpperCase();
}

function extFromMime(type: string) {
  const map: Record<string, string> = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/webp": "webp",
    "image/gif": "gif",
    "image/bmp": "bmp",
    "application/pdf": "pdf",
  };
  if (map[type]) return map[type];
  if (type.startsWith("image/")) return type.slice(6) || "png";
  return "bin";
}

function fileMatchesAccept(file: File, accept: string): boolean {
  const parts = accept
    .split(",")
    .map((s) => s.trim().toLowerCase())
    .filter(Boolean);
  if (!parts.length) return true;
  const name = (file.name || "").toLowerCase();
  const type = (file.type || "").toLowerCase();
  return parts.some((part) => {
    if (part.endsWith("/*")) {
      return type.startsWith(part.slice(0, -1));
    }
    if (part.startsWith(".")) {
      return name.endsWith(part) || type.endsWith(part.slice(1));
    }
    return type === part;
  });
}

function filesFromClipboard(data: DataTransfer | null): File[] {
  if (!data) return [];
  const out: File[] = [];
  const seen = new Set<string>();

  const push = (file: File | null) => {
    if (!file) return;
    const key = `${file.type}:${file.size}:${file.name}`;
    if (seen.has(key)) return;
    seen.add(key);
    out.push(file);
  };

  if (data.items) {
    for (const item of Array.from(data.items)) {
      if (item.kind !== "file") continue;
      push(item.getAsFile());
    }
  }
  if (!out.length && data.files?.length) {
    for (const file of Array.from(data.files)) push(file);
  }
  return out;
}

function namedClipboardFile(file: File): File {
  const name = (file.name || "").trim();
  if (name && name !== "image.png" && name !== "image.jpg") return file;
  const ext = extFromMime(file.type || "image/png");
  return new File([file], `pasted-${Date.now()}.${ext}`, {
    type: file.type || `image/${ext}`,
    lastModified: file.lastModified,
  });
}

export type AttachmentProps = {
  accept: string;
  multiple?: boolean;
  inputRef: RefObject<HTMLInputElement | null>;
  fileNames: string[];
  onFilesChange: () => void;
};

type AttachmentPreview = {
  name: string;
  url: string | null;
  isImage: boolean;
};

export function PromptBar({
  placeholder,
  busy,
  extra,
  attachment,
  canSubmit,
  draft,
  draftNonce = 0,
  onSubmit,
  onStop,
}: {
  placeholder: string;
  busy?: boolean;
  extra?: ReactNode;
  attachment?: AttachmentProps;
  canSubmit?: (value: string) => boolean;
  /** Prefill the input (e.g. edit message). Remounts when draftNonce changes. */
  draft?: string;
  draftNonce?: number;
  onSubmit: (value: string) => void;
  onStop?: () => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [previews, setPreviews] = useState<AttachmentPreview[]>([]);

  useEffect(() => {
    if (draftNonce <= 0 || draft == null) return;
    const input = inputRef.current;
    if (!input) return;
    input.value = draft;
    input.focus();
    const len = draft.length;
    input.setSelectionRange(len, len);
  }, [draft, draftNonce]);

  useEffect(() => {
    const names = attachment?.fileNames ?? [];
    if (!attachment || !names.length) {
      setPreviews([]);
      return;
    }
    const files = attachment.inputRef.current?.files
      ? Array.from(attachment.inputRef.current.files)
      : [];
    const next: AttachmentPreview[] = names.map((name, i) => {
      const file = files[i];
      const isImage = Boolean(file?.type.startsWith("image/"));
      return {
        name,
        isImage,
        url: file && isImage ? URL.createObjectURL(file) : null,
      };
    });
    setPreviews(next);
    return () => {
      for (const p of next) {
        if (p.url) URL.revokeObjectURL(p.url);
      }
    };
    // fileNames contents drive previews; avoid depending on attachment object identity
    // eslint-disable-next-line react-hooks/exhaustive-deps -- names joined is the stable key
  }, [attachment?.fileNames.join("\0")]);

  function handle(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (busy) return;
    const form = e.currentTarget;
    const input = form.elements.namedItem("lab-prompt") as HTMLInputElement | null;
    if (!input) return;
    const value = input.value.trim();
    const allowed = canSubmit ? canSubmit(value) : value.length > 0;
    if (!allowed) return;
    onSubmit(value);
    input.value = "";
  }

  function removeAttachment(index: number) {
    if (!attachment) return;
    const fileInput = attachment.inputRef.current;
    if (!fileInput?.files) return;
    const dt = new DataTransfer();
    Array.from(fileInput.files).forEach((file, i) => {
      if (i !== index) dt.items.add(file);
    });
    fileInput.files = dt.files;
    attachment.onFilesChange();
  }

  function applyFiles(next: File[]) {
    if (!attachment) return;
    const fileInput = attachment.inputRef.current;
    if (!fileInput) return;
    const dt = new DataTransfer();
    for (const file of next) dt.items.add(file);
    fileInput.files = dt.files;
    attachment.onFilesChange();
  }

  function onPaste(e: ClipboardEvent<HTMLInputElement>) {
    if (!attachment || busy) return;
    const pasted = filesFromClipboard(e.clipboardData)
      .filter((f) => fileMatchesAccept(f, attachment.accept))
      .map(namedClipboardFile);
    if (!pasted.length) return;

    // Attach matching files; leave text-only pastes alone.
    e.preventDefault();
    if (attachment.multiple) {
      const existing = attachment.inputRef.current?.files
        ? Array.from(attachment.inputRef.current.files)
        : [];
      applyFiles([...existing, ...pasted]);
      return;
    }
    applyFiles([pasted[pasted.length - 1]]);
  }

  return (
    <form onSubmit={handle} className="space-y-2" autoComplete="off">
      {extra}
      {attachment && previews.length ? (
        <div className="flex flex-wrap gap-2 px-0.5">
          {previews.map((item, index) => (
            <div
              key={`${item.name}-${index}`}
              className="relative flex max-w-[min(100%,18rem)] items-center gap-2.5 rounded-xl border border-[var(--line)] bg-[var(--surface)] py-2 pl-2 pr-8"
            >
              {item.isImage && item.url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={item.url}
                  alt=""
                  className="h-12 w-12 shrink-0 rounded-md object-cover ring-1 ring-[var(--line)]"
                />
              ) : (
                <FileTypeIcon ext={fileExt(item.name)} />
              )}
              <div className="min-w-0">
                <p
                  className="truncate text-sm text-[var(--txt)]"
                  title={item.name}
                >
                  {item.name}
                </p>
                <p className="font-mono text-[11px] text-[var(--txt3)]">
                  {displayType(fileExt(item.name))}
                </p>
              </div>
              <button
                type="button"
                disabled={busy}
                onClick={() => removeAttachment(index)}
                aria-label={`Remove ${item.name}`}
                className="absolute -right-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full border border-[var(--line)] bg-[var(--bg2)] text-[var(--txt2)] hover:bg-[var(--surface)] hover:text-[var(--txt)] disabled:opacity-50"
              >
                <CloseIcon />
              </button>
            </div>
          ))}
        </div>
      ) : null}
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
              title="Attach file"
              className="shrink-0 rounded-xl p-2 hover:bg-[var(--bg)] disabled:opacity-60"
            >
              <AttachIcon />
            </button>
          </>
        ) : null}
        <input
          ref={inputRef}
          key={draftNonce > 0 ? `draft-${draftNonce}` : "prompt"}
          name="lab-prompt"
          type="text"
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="off"
          spellCheck={false}
          disabled={busy}
          defaultValue={draftNonce > 0 ? draft : undefined}
          placeholder={placeholder}
          onPaste={onPaste}
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
    </form>
  );
}
