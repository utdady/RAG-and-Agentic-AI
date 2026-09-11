"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import type { Demo } from "@/lib/demos";
import { GITHUB_BASE } from "@/lib/demos";
import {
  checkApiHealth,
  formatFetchError,
  hubEventError,
  isAbortError,
  readSse,
  runDemo,
  type HubEvent,
} from "@/lib/sse";
import { ContextCards, type ContextItem } from "./ContextCards";
import { DatasetGuide } from "./DatasetGuide";
import { MessageActions } from "./MessageActions";
import { PromptBar } from "./PromptBar";
import { StreamingText } from "./StreamingText";
import {
  StatusTimeline,
  appendThinkingStep,
  finalizeStatusSteps,
  upsertTaskStep,
  upsertToolStep,
  type StatusStep,
} from "./StatusTimeline";

type Props = { demo: Demo };

type Turn = {
  id: string;
  user: string;
  text: string;
  images: string[];
  error?: string;
};

function formatElapsed(ms: number) {
  const sec = Math.max(0, Math.floor(ms / 1000));
  if (sec < 60) return `${sec}s`;
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}m ${s}s`;
}

function UserBubble({
  text,
  onEdit,
  disabled,
}: {
  text: string;
  onEdit?: () => void;
  disabled?: boolean;
}) {
  return (
    <div className="flex flex-col items-end gap-1">
      <div className="max-w-[min(85%,42rem)] rounded-2xl rounded-tr-sm border border-[var(--line)] bg-[var(--surface)] px-4 py-3 text-sm">
        {text}
      </div>
      <MessageActions
        align="end"
        copyText={text}
        onEdit={onEdit}
        disabled={disabled}
      />
    </div>
  );
}

function AssistantBubble({
  text,
  error,
  showActions,
}: {
  text: string;
  error?: string;
  showActions?: boolean;
}) {
  if (error) {
    return (
      <div className="flex flex-col items-start gap-1">
        <p className="max-w-[min(92%,48rem)] whitespace-pre-line rounded-2xl rounded-tl-sm border border-[var(--warn)]/40 bg-[var(--warn)]/10 px-4 py-3 text-sm text-[var(--warn)]">
          {error}
        </p>
        {showActions ? (
          <MessageActions align="start" copyText={error} />
        ) : null}
      </div>
    );
  }
  if (!text) return null;
  return (
    <div className="flex flex-col items-start gap-1">
      <div className="max-w-[min(92%,48rem)] rounded-2xl rounded-tl-sm border border-[var(--line)] bg-[var(--bg2)] px-4 py-3">
        <StreamingText text={text} />
      </div>
      {showActions ? (
        <MessageActions align="start" copyText={text} />
      ) : null}
    </div>
  );
}

export function DemoWorkspace({ demo }: Props) {
  const fileRef = useRef<HTMLInputElement>(null);
  const turnId = useRef(0);
  const abortRef = useRef<AbortController | null>(null);
  const startedAt = useRef<number | null>(null);
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const [busy, setBusy] = useState(false);
  const [elapsed, setElapsed] = useState("");
  const [history, setHistory] = useState<Turn[]>([]);
  const [userMessage, setUserMessage] = useState("");
  const [statusSteps, setStatusSteps] = useState<StatusStep[]>([]);
  const [contexts, setContexts] = useState<ContextItem[]>([]);
  const [text, setText] = useState("");
  const [images, setImages] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [mode, setMode] = useState("symptoms");
  const [workflow, setWorkflow] = useState("recipe");
  const [url, setUrl] = useState("");
  const [fileNames, setFileNames] = useState<string[]>([]);
  const [draft, setDraft] = useState("");
  const [draftNonce, setDraftNonce] = useState(0);

  useEffect(() => {
    if (!busy) return;
    startedAt.current = Date.now();
    setElapsed("0s");
    const id = window.setInterval(() => {
      if (!startedAt.current) return;
      setElapsed(formatElapsed(Date.now() - startedAt.current));
    }, 1000);
    return () => window.clearInterval(id);
  }, [busy]);

  useEffect(() => {
    if (!userMessage && !busy && !text) return;
    chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [userMessage, busy, text, error, statusSteps.length]);

  function resetAssistant() {
    setStatusSteps([]);
    setContexts([]);
    setText("");
    setImages([]);
    setElapsed("");
    startedAt.current = null;
  }

  function archiveTurn() {
    if (!userMessage) return;
    turnId.current += 1;
    setHistory((prev) => [
      ...prev,
      {
        id: `turn-${turnId.current}`,
        user: userMessage,
        text,
        images: [...images],
        error: error || undefined,
      },
    ]);
  }

  function applyEvent(ev: HubEvent) {
    if (ev.type === "thinking" && ev.label) {
      setStatusSteps((s) => appendThinkingStep(s, ev.label!));
    } else if (ev.type === "task" && ev.id && ev.name) {
      setStatusSteps((s) => upsertTaskStep(s, ev.id!, ev.name!, ev.status));
    } else if (ev.type === "context" && ev.title && ev.snippet) {
      setContexts((c) => [
        ...c,
        { title: ev.title!, snippet: ev.snippet!, source: ev.source },
      ]);
    } else if (ev.type === "tool" && ev.name) {
      setStatusSteps((s) => upsertToolStep(s, ev.name!, ev.status));
    } else if (ev.type === "token" && ev.text) {
      setStatusSteps((s) => finalizeStatusSteps(s));
      setText((s) => s + ev.text);
    } else if (ev.type === "image" && ev.data) {
      setStatusSteps((s) => finalizeStatusSteps(s));
      const mime = ev.mime || "image/png";
      setImages((imgs) => [...imgs, `data:${mime};base64,${ev.data}`]);
    } else if (ev.type === "error") {
      setStatusSteps((s) => finalizeStatusSteps(s));
      setError(hubEventError(ev));
    } else if (ev.type === "done") {
      setStatusSteps((s) => finalizeStatusSteps(s));
    }
  }

  const needsFile = ["pdf", "docs", "image", "audio"].includes(demo.kind);
  const fileAccept =
    demo.kind === "pdf"
      ? ".pdf"
      : demo.kind === "audio"
        ? "audio/*"
        : demo.kind === "image"
          ? "image/*"
          : ".pdf,.docx,.txt,.md";

  function hasFiles() {
    return fileNames.length > 0;
  }

  function onFilesChange() {
    const files = fileRef.current?.files;
    setFileNames(files ? Array.from(files).map((f) => f.name) : []);
  }

  function canSubmitMessage(message: string) {
    const trimmed = message.trim();
    // Doc / PDF demos need both an attachment and a real question.
    if (demo.kind === "docs" || demo.kind === "pdf") {
      return hasFiles() && trimmed.length > 0;
    }
    if (trimmed) return true;
    if (needsFile && hasFiles()) return true;
    if (demo.kind === "youtube" && url.trim()) return true;
    return false;
  }

  function displayLabel(message: string, extra?: Record<string, string>) {
    const trimmed = message.trim();
    if (trimmed) return trimmed;
    if (extra?.meal_name) return `Plan meal: ${extra.meal_name}`;
    if (needsFile && hasFiles()) {
      const names = Array.from(fileRef.current?.files ?? []).map((f) => f.name);
      return names.length ? `Uploaded: ${names.join(", ")}` : "Uploaded file";
    }
    if (demo.kind === "youtube" && url.trim()) return url.trim();
    return "";
  }

  function stopRun() {
    const controller = abortRef.current;
    if (!controller) return;
    controller.abort();
    setBusy(false);
    setStatusSteps((s) => finalizeStatusSteps(s));
    setError((prev) => prev || "Stopped.");
  }

  function beginEdit(message: string, historyIndex?: number) {
    if (busy || demo.kind === "form") return;
    abortRef.current?.abort();
    if (typeof historyIndex === "number") {
      setHistory((prev) => prev.slice(0, historyIndex));
      setUserMessage("");
      resetAssistant();
      setError("");
    } else {
      // Editing the in-flight / latest user turn
      setUserMessage("");
      resetAssistant();
      setError("");
    }
    setDraft(message);
    setDraftNonce((n) => n + 1);
  }

  async function submit(message: string, extra?: Record<string, string>) {
    const label = displayLabel(message, extra);
    if (!label && !canSubmitMessage(message)) return;

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    archiveTurn();
    setUserMessage(label || message.trim());
    resetAssistant();
    setError("");
    setBusy(true);
    setStatusSteps([
      {
        key: "status-start",
        kind: "status",
        label: "Starting demo…",
        status: "running",
      },
    ]);
    let gotTokens = false;
    let gotImages = false;
    let gotError = false;
    let sawDone = false;
    try {
      const healthy = await checkApiHealth(controller.signal);
      if (controller.signal.aborted) {
        setError("Stopped.");
        return;
      }
      if (!healthy) {
        setError(
          "Can't load the demo\n\nThe demo hub isn't responding. Refresh the page and try again.",
        );
        gotError = true;
        return;
      }
      setStatusSteps((s) =>
        s.map((step) =>
          step.key === "status-start"
            ? {
                ...step,
                label: "Connected — running pipeline",
                status: "done",
              }
            : step,
        ),
      );
      const form = new FormData();
      form.set("message", message);
      const ytUrl = url || (message.startsWith("http") ? message : "");
      if (ytUrl) form.set("url", ytUrl);
      form.set("mode", mode);
      form.set("workflow", workflow);
      if (extra) {
        for (const [k, v] of Object.entries(extra)) form.set(k, v);
      }
      const files = fileRef.current?.files;
      if (files) {
        for (const f of Array.from(files)) form.append("files", f);
      }
      if (controller.signal.aborted) {
        setError("Stopped.");
        return;
      }
      const res = await runDemo(demo.slug, form, controller.signal);
      if (controller.signal.aborted) {
        setError("Stopped.");
        return;
      }
      try {
        for await (const ev of readSse(res, controller.signal)) {
          if (controller.signal.aborted) break;
          if (ev.type === "token" && ev.text) gotTokens = true;
          if (ev.type === "image" && ev.data) gotImages = true;
          if (ev.type === "error") gotError = true;
          applyEvent(ev);
          if (ev.type === "done") {
            sawDone = true;
            break;
          }
        }
        if (controller.signal.aborted) {
          if (!gotTokens && !gotImages) setError("Stopped.");
        } else if (!gotTokens && !gotImages && !gotError) {
          setError(
            formatFetchError(
              new Error(sawDone ? "empty" : "truncated"),
              "stream",
            ),
          );
          gotError = true;
        }
      } catch (streamErr) {
        if (controller.signal.aborted || isAbortError(streamErr)) {
          if (!gotTokens && !gotImages) setError("Stopped.");
        } else if (!gotTokens && !gotImages) {
          setError(formatFetchError(streamErr, "stream"));
          gotError = true;
        }
        return;
      }
    } catch (e) {
      if (controller.signal.aborted || isAbortError(e)) {
        if (!gotTokens && !gotImages) setError("Stopped.");
      } else {
        setError(formatFetchError(e, "connect"));
      }
    } finally {
      setStatusSteps((s) => finalizeStatusSteps(s));
      setBusy(false);
      if (abortRef.current === controller) {
        abortRef.current = null;
      }
    }
  }

  const extraFields = (
    <div className="space-y-3">
      {demo.kind === "youtube" ? (
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://www.youtube.com/watch?v=…"
          className="w-full rounded-xl border border-[var(--line)] bg-[var(--surface)] px-3 py-2 text-sm outline-none"
        />
      ) : null}
      {demo.kind === "healthcare" ? (
        <select
          value={mode}
          onChange={(e) => setMode(e.target.value)}
          className="w-full rounded-xl border border-[var(--line)] bg-[var(--surface)] px-3 py-2 text-sm"
        >
          <option value="symptoms">Symptom consultation</option>
          <option value="mental">Mental health (educational)</option>
        </select>
      ) : null}
      {demo.slug === "nourishbot" ? (
        <select
          value={workflow}
          onChange={(e) => setWorkflow(e.target.value)}
          className="w-full rounded-xl border border-[var(--line)] bg-[var(--surface)] px-3 py-2 text-sm"
        >
          <option value="recipe">Recipe from photo</option>
          <option value="analysis">Nutrition analysis</option>
        </select>
      ) : null}
    </div>
  );

  function onFormSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const extraForm: Record<string, string> = {};
    for (const [k, v] of fd.entries()) {
      if (typeof v === "string") extraForm[k] = v;
    }
    void submit(String(fd.get("meal_name") || ""), extraForm);
  }

  const hasExtraFields =
    demo.kind === "youtube" ||
    demo.kind === "healthcare" ||
    demo.slug === "nourishbot";

  const showTimeline = busy || statusSteps.length > 0;

  return (
    <div className="flex h-full min-h-0 flex-1 flex-col text-left lg:min-h-0">
      <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-6 pt-6 lg:px-10 lg:pt-10">
        <div className="mx-auto w-full max-w-4xl">
          <header className="mb-6 space-y-3">
            <h2 className="font-display text-2xl font-bold">{demo.title}</h2>
            <p className="text-sm text-[var(--txt2)]">{demo.tagline}</p>
            {demo.description ? (
              <p className="text-sm leading-relaxed text-[var(--txt2)]/90">
                {demo.description}
              </p>
            ) : null}
            {demo.tips?.length ? (
              <div className="space-y-1.5">
                <p className="text-xs font-medium uppercase tracking-wide text-[var(--txt2)]">
                  How to get good results
                </p>
                <ul className="list-disc space-y-1 pl-4 text-sm leading-relaxed text-[var(--txt2)]/90">
                  {demo.tips.map((tip) => (
                    <li key={tip}>{tip}</li>
                  ))}
                </ul>
              </div>
            ) : null}
            <div className="flex flex-wrap gap-2">
              {demo.tags.map((t) => (
                <span
                  key={t}
                  className="rounded-md border border-[var(--line)] px-2 py-0.5 font-mono text-[11px] text-accent"
                >
                  {t}
                </span>
              ))}
              <a
                className="text-sm text-[var(--txt2)] underline decoration-[var(--line)] hover:text-accent"
                href={`${GITHUB_BASE}/${demo.github}`}
                target="_blank"
                rel="noopener noreferrer"
              >
                Source
              </a>
            </div>
            {demo.kind === "healthcare" ? (
              <p className="rounded-lg border border-[var(--warn)]/40 bg-[var(--warn)]/10 px-3 py-2 text-sm text-[var(--warn)]">
                Educational demo only — not medical or mental-health care.
              </p>
            ) : null}
          </header>

          {demo.guide ? (
            <div className="mb-6">
              <DatasetGuide
                blurb={demo.guide.blurb}
                tables={demo.guide.tables}
                starters={demo.guide.starters}
                busy={busy}
                onStarter={(prompt) => {
                  void submit(prompt);
                }}
              />
            </div>
          ) : null}

          <div className="flex flex-col gap-4 pb-6">
            {history.map((turn, index) => (
              <div key={turn.id} className="space-y-4">
                <UserBubble
                  text={turn.user}
                  disabled={busy}
                  onEdit={
                    demo.kind === "form"
                      ? undefined
                      : () => beginEdit(turn.user, index)
                  }
                />
                <AssistantBubble
                  text={turn.text}
                  error={turn.error}
                  showActions
                />
                {turn.images.map((src, i) => (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    key={`${turn.id}-img-${i}`}
                    src={src}
                    alt="Demo output"
                    className="max-h-80 rounded-xl border border-[var(--line)]"
                  />
                ))}
              </div>
            ))}

            {userMessage ? (
              <div className="space-y-4">
                <UserBubble
                  text={userMessage}
                  disabled={busy}
                  onEdit={
                    demo.kind === "form" || busy
                      ? undefined
                      : () => beginEdit(userMessage)
                  }
                />
                {showTimeline ? (
                  <StatusTimeline
                    steps={statusSteps}
                    busy={busy && !text && !images.length && !error}
                    elapsed={elapsed || undefined}
                  />
                ) : null}
                <ContextCards items={contexts} />
                <AssistantBubble
                  text={text}
                  error={error || undefined}
                  showActions={!busy && Boolean(text || error)}
                />
                {images.map((src, i) => (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    key={`current-img-${i}`}
                    src={src}
                    alt="Demo output"
                    className="max-h-80 rounded-xl border border-[var(--line)]"
                  />
                ))}
              </div>
            ) : null}
            <div ref={chatEndRef} />
          </div>
        </div>
      </div>

      <div className="shrink-0 border-t border-[var(--line)] bg-[var(--bg)] px-6 py-4 lg:px-10">
        <div className="mx-auto w-full max-w-4xl">
          {demo.kind === "form" ? (
            <form
              onSubmit={onFormSubmit}
              className="grid gap-3 rounded-2xl border border-[var(--line)] bg-[var(--surface)] p-4"
            >
              <input
                name="meal_name"
                defaultValue="weeknight pasta"
                placeholder="Meal"
                className="rounded-lg border border-[var(--line)] bg-[var(--bg)] px-3 py-2 text-sm"
              />
              <input
                name="servings"
                defaultValue="4"
                className="rounded-lg border border-[var(--line)] bg-[var(--bg)] px-3 py-2 text-sm"
              />
              <input
                name="budget"
                defaultValue="moderate"
                className="rounded-lg border border-[var(--line)] bg-[var(--bg)] px-3 py-2 text-sm"
              />
              <input
                name="dietary"
                placeholder="dietary restrictions"
                className="rounded-lg border border-[var(--line)] bg-[var(--bg)] px-3 py-2 text-sm"
              />
              <input
                name="cooking_skill"
                defaultValue="intermediate"
                className="rounded-lg border border-[var(--line)] bg-[var(--bg)] px-3 py-2 text-sm"
              />
              {busy ? (
                <button
                  type="button"
                  onClick={stopRun}
                  className="rounded-xl border border-[var(--warn)]/50 bg-[var(--warn)]/15 px-4 py-2 text-sm font-medium text-[var(--warn)] hover:bg-[var(--warn)]/25"
                >
                  Stop
                </button>
              ) : (
                <button
                  type="submit"
                  className="rounded-xl bg-accent px-4 py-2 text-sm font-medium text-black"
                >
                  Plan meal
                </button>
              )}
            </form>
          ) : (
            <PromptBar
              placeholder={demo.placeholder || "Write a message…"}
              busy={busy}
              draft={draft}
              draftNonce={draftNonce}
              extra={hasExtraFields ? extraFields : undefined}
              attachment={
                needsFile
                  ? {
                      accept: fileAccept,
                      multiple: demo.kind === "docs",
                      inputRef: fileRef,
                      fileNames,
                      onFilesChange,
                    }
                  : undefined
              }
              canSubmit={canSubmitMessage}
              onSubmit={(v) => {
                void submit(v);
              }}
              onStop={stopRun}
            />
          )}
        </div>
      </div>
    </div>
  );
}
