"use client";

import { useRef, useState, type FormEvent } from "react";
import type { Demo } from "@/lib/demos";
import { GITHUB_BASE } from "@/lib/demos";
import { checkApiHealth, formatFetchError, hubEventError, isAbortError, readSse, runDemo, type HubEvent } from "@/lib/sse";
import { ContextCards, type ContextItem } from "./ContextCards";
import { LoadingState } from "./LoadingState";
import { PromptBar } from "./PromptBar";
import { StreamingText } from "./StreamingText";
import { TaskRows, type TaskItem } from "./TaskRows";
import { ThinkingTrace } from "./Thinking";
import { ToolChips, type ToolItem } from "./ToolChips";

type Props = { demo: Demo };

type Turn = {
  id: string;
  user: string;
  text: string;
  images: string[];
  error?: string;
};

function UserBubble({ text }: { text: string }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[85%] rounded-2xl rounded-tr-sm border border-[var(--line)] bg-[var(--surface)] px-4 py-3 text-sm">
        {text}
      </div>
    </div>
  );
}

function AssistantBubble({
  text,
  error,
}: {
  text: string;
  error?: string;
}) {
  if (error) {
    return (
      <div className="flex justify-start">
        <p className="max-w-[90%] whitespace-pre-line rounded-2xl rounded-tl-sm border border-[var(--warn)]/40 bg-[var(--warn)]/10 px-4 py-3 text-sm text-[var(--warn)]">
          {error}
        </p>
      </div>
    );
  }
  if (!text) return null;
  return (
    <div className="flex justify-start">
      <div className="max-w-[90%] rounded-2xl rounded-tl-sm border border-[var(--line)] bg-[var(--bg2)] px-4 py-3">
        <StreamingText text={text} />
      </div>
    </div>
  );
}

export function DemoWorkspace({ demo }: Props) {
  const fileRef = useRef<HTMLInputElement>(null);
  const turnId = useRef(0);
  const abortRef = useRef<AbortController | null>(null);
  const [busy, setBusy] = useState(false);
  const [history, setHistory] = useState<Turn[]>([]);
  const [userMessage, setUserMessage] = useState("");
  const [thinking, setThinking] = useState<string[]>([]);
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [contexts, setContexts] = useState<ContextItem[]>([]);
  const [tools, setTools] = useState<ToolItem[]>([]);
  const [text, setText] = useState("");
  const [images, setImages] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [mode, setMode] = useState("symptoms");
  const [workflow, setWorkflow] = useState("recipe");
  const [url, setUrl] = useState("");
  const [fileNames, setFileNames] = useState<string[]>([]);

  function resetAssistant() {
    setThinking([]);
    setTasks([]);
    setContexts([]);
    setTools([]);
    setText("");
    setImages([]);
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

  function clearProgress() {
    setThinking([]);
    setTasks([]);
    setTools([]);
  }

  function applyEvent(ev: HubEvent) {
    if (ev.type === "thinking" && ev.label) {
      setThinking((s) => [...s, ev.label!]);
    } else if (ev.type === "task" && ev.id && ev.name) {
      setTasks((prev) => {
        const rest = prev.filter((t) => t.id !== ev.id);
        return [...rest, { id: ev.id!, name: ev.name!, status: ev.status || "running" }];
      });
    } else if (ev.type === "context" && ev.title && ev.snippet) {
      setContexts((c) => [
        ...c,
        { title: ev.title!, snippet: ev.snippet!, source: ev.source },
      ]);
    } else if (ev.type === "tool" && ev.name) {
      setTools((t) => [...t, { name: ev.name!, status: ev.status }]);
    } else if (ev.type === "token" && ev.text) {
      clearProgress();
      setText((s) => s + ev.text);
    } else if (ev.type === "image" && ev.data) {
      clearProgress();
      const mime = ev.mime || "image/png";
      setImages((imgs) => [...imgs, `data:${mime};base64,${ev.data}`]);
    } else if (ev.type === "error") {
      clearProgress();
      setError(hubEventError(ev));
    } else if (ev.type === "done") {
      clearProgress();
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
    if (message.trim()) return true;
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
    abortRef.current?.abort();
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
    let gotTokens = false;
    try {
      const healthy = await checkApiHealth();
      if (!healthy) {
        setError(
          "Can't load the demo\n\nThe demo hub isn't responding. Refresh the page and try again.",
        );
        return;
      }
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
      const res = await runDemo(demo.slug, form, controller.signal);
      try {
        for await (const ev of readSse(res, controller.signal)) {
          if (ev.type === "token") gotTokens = true;
          applyEvent(ev);
          if (ev.type === "done") break;
        }
      } catch (streamErr) {
        if (!isAbortError(streamErr) && !gotTokens) {
          setError(formatFetchError(streamErr, "stream"));
        }
        return;
      }
    } catch (e) {
      if (isAbortError(e)) {
        if (!gotTokens) setError("Stopped.");
      } else {
        setError(formatFetchError(e, "connect"));
      }
    } finally {
      clearProgress();
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

  return (
    <div className="flex h-full min-h-[calc(100dvh-3.5rem)] flex-col text-left lg:min-h-screen">
      <header className="shrink-0 space-y-3 px-6 pt-6 lg:px-10 lg:pt-10">
        <h2 className="text-2xl font-semibold">{demo.title}</h2>
        <p className="text-sm text-[var(--txt2)]">{demo.tagline}</p>
        {demo.description ? (
          <p className="max-w-2xl text-sm leading-relaxed text-[var(--txt2)]/90">
            {demo.description}
          </p>
        ) : null}
        {demo.tips?.length ? (
          <div className="max-w-2xl space-y-1.5">
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

      <div className="mt-6 flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto px-6 lg:px-10">
        {history.map((turn) => (
          <div key={turn.id} className="space-y-4">
            <UserBubble text={turn.user} />
            <AssistantBubble text={turn.text} error={turn.error} />
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
            <UserBubble text={userMessage} />
            {busy && !text && !images.length ? (
              <>
                <LoadingState thinking />
                <ThinkingTrace steps={thinking} />
                <TaskRows tasks={tasks} />
                <ToolChips tools={tools} />
              </>
            ) : null}
            <ContextCards items={contexts} />
            <AssistantBubble text={text} error={error || undefined} />
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
      </div>

      <div className="shrink-0 border-t border-[var(--line)] bg-[var(--bg)] px-6 py-4 lg:px-10">
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
            placeholder="Write a message…"
            busy={busy}
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
  );
}
