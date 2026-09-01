import {
  formatErrorDisplay,
  humanizeError,
  type FriendlyError,
} from "./errors";

export type HubEvent = {
  type:
    | "thinking"
    | "task"
    | "context"
    | "tool"
    | "token"
    | "followup"
    | "image"
    | "error"
    | "done";
  label?: string;
  id?: string;
  name?: string;
  status?: string;
  title?: string;
  snippet?: string;
  source?: string;
  text?: string;
  suggestions?: string[];
  mime?: string;
  data?: string;
  message?: string;
};

export function apiBase() {
  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    if (
      host === "localhost" ||
      host === "127.0.0.1" ||
      host === "[::1]"
    ) {
      return "/api/hub";
    }
    return process.env.NEXT_PUBLIC_API_URL || "/api/hub";
  }
  return process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080";
}

export async function checkApiHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${apiBase()}/health`, { cache: "no-store" });
    if (!res.ok) return false;
    const data = (await res.json()) as { ok?: boolean };
    return data.ok === true;
  } catch {
    return false;
  }
}

export function hubEventError(ev: HubEvent): string {
  const raw = ev.message || "Request failed";
  const friendly = humanizeError(raw, ev.title);
  return formatErrorDisplay(friendly);
}

function formatFetchError(
  err: unknown,
  phase: "connect" | "stream" = "connect",
): string {
  if (phase === "stream") {
    return formatErrorDisplay({
      title: "Response interrupted",
      message: "The answer didn't finish loading. Please run your question again.",
    });
  }
  if (err instanceof TypeError) {
    return formatErrorDisplay({
      title: "Can't load the demo",
      message: "The demo hub isn't responding. Refresh the page and try again.",
    });
  }
  if (err instanceof Error) {
    return formatErrorDisplay(humanizeError(err.message));
  }
  return formatErrorDisplay({
    title: "Something went wrong",
    message: "We couldn't complete your request. Please try again in a moment.",
  });
}

export async function* readSse(
  res: Response,
  signal?: AbortSignal,
): AsyncGenerator<HubEvent> {
  const reader = res.body?.getReader();
  if (!reader) return;
  const decoder = new TextDecoder();
  let buf = "";
  try {
    while (true) {
      if (signal?.aborted) {
        await reader.cancel();
        break;
      }
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      const chunks = buf.split("\n\n");
      buf = chunks.pop() || "";
      for (const chunk of chunks) {
        const line = chunk.split("\n").find((l) => l.startsWith("data: "));
        if (!line) continue;
        try {
          yield JSON.parse(line.slice(6)) as HubEvent;
        } catch {
          /* skip malformed */
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

export { formatFetchError, humanizeError, formatErrorDisplay };
export type { FriendlyError };

export async function runDemo(
  slug: string,
  form: FormData,
  signal?: AbortSignal,
) {
  const res = await fetch(`${apiBase()}/demos/${slug}/run`, {
    method: "POST",
    body: form,
    signal,
  });
  if (!res.ok) {
    throw new Error(
      formatErrorDisplay({
        title: "Can't load the demo",
        message: "The demo hub isn't responding. Refresh the page and try again.",
      }),
    );
  }
  return res;
}

export function isAbortError(err: unknown) {
  return (
    (err instanceof DOMException && err.name === "AbortError") ||
    (err instanceof Error && err.name === "AbortError")
  );
}
