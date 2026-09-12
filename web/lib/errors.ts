export type FriendlyError = {
  title: string;
  message: string;
};

function waitSeconds(raw: string): number | null {
  const minMatch = raw.match(/try again in (\d+(?:\.\d+)?)\s*m/i);
  if (minMatch) return Number(minMatch[1]) * 60;
  const secMatch = raw.match(/try again in (\d+(?:\.\d+)?)\s*s/i);
  if (secMatch) return Number(secMatch[1]);
  return null;
}

function usagePercent(raw: string): number | null {
  const match = raw.match(/limit\s+(\d+(?:\.\d+)?)[\s\S]{0,80}?used\s+(\d+(?:\.\d+)?)/i);
  if (!match) return null;
  const limit = Number(match[1]);
  const used = Number(match[2]);
  if (!(limit > 0)) return null;
  return Math.max(1, Math.min(100, Math.round((100 * used) / limit)));
}

function formatClock(date: Date): string {
  let hour = date.getHours() % 12;
  if (hour === 0) hour = 12;
  const minutes = String(date.getMinutes()).padStart(2, "0");
  const ampm = date.getHours() < 12 ? "AM" : "PM";
  return `${hour}:${minutes} ${ampm}`;
}

function refreshHint(raw: string): string {
  const seconds = waitSeconds(raw);
  if (seconds == null) return " Try again later today.";
  const when = new Date(Date.now() + seconds * 1000);
  if (seconds >= 3600) {
    const hours = Math.max(1, Math.round(seconds / 3600));
    return (
      ` It refreshes around ${formatClock(when)} ` +
      `(in about ${hours} hour${hours === 1 ? "" : "s"}).`
    );
  }
  if (seconds >= 60) {
    const minutes = Math.max(1, Math.round(seconds / 60));
    return (
      ` It refreshes around ${formatClock(when)} ` +
      `(in about ${minutes} minute${minutes === 1 ? "" : "s"}).`
    );
  }
  const secs = Math.max(5, Math.round(seconds));
  return ` Please try again in about ${secs} seconds.`;
}

function waitHint(raw: string): string {
  const seconds = waitSeconds(raw);
  if (seconds == null) return " Please try again in a few minutes.";
  if (seconds >= 60) {
    const minutes = Math.max(1, Math.round(seconds / 60));
    return ` Please try again in about ${minutes} minute${minutes === 1 ? "" : "s"}.`;
  }
  const secs = Math.max(5, Math.round(seconds));
  return ` Please try again in about ${secs} seconds.`;
}

function dailyUsageMessage(raw: string): string {
  const pct = usagePercent(raw);
  const capacity =
    pct != null
      ? `Shared demo capacity is full for now (${pct}% of today's allowance).`
      : "Shared demo capacity is full for now (100% of today's allowance).";
  return capacity + refreshHint(raw) + " Try again after that.";
}

function parseError(): FriendlyError {
  return {
    title: "Couldn't finish the response",
    message: "The demo had trouble reading the model output. Please try again.",
  };
}

function looksTechnical(raw: string): boolean {
  const lower = raw.toLowerCase();
  return (
    raw.includes("Error code:") ||
    raw.includes("{") ||
    lower.includes("groq") ||
    lower.includes("api key") ||
    lower.includes("uvicorn") ||
    lower.includes("fastapi") ||
    lower.includes("org_") ||
    lower.includes("rate_limit_exceeded") ||
    lower.includes("jsondecodeerror") ||
    (lower.includes("expecting") && lower.includes("delimiter"))
  );
}

export function humanizeError(raw: string, title?: string): FriendlyError {
  if (title && !looksTechnical(raw)) {
    return { title, message: raw };
  }

  const lower = raw.toLowerCase();

  if (raw.includes("429") || lower.includes("rate limit") || lower.includes("rate_limit")) {
    const waitS = waitSeconds(raw) ?? 0;
    const daily =
      lower.includes("tokens per day") ||
      lower.includes("tpd") ||
      lower.includes("per day") ||
      lower.includes("rpd") ||
      waitS >= 3600;
    if (daily) {
      return {
        title: "Demo usage limit reached",
        message: dailyUsageMessage(raw),
      };
    }
    return {
      title: "Please wait a moment",
      message: "The demo is getting a lot of requests right now." + waitHint(raw),
    };
  }

  if (lower.includes("groq_api_key") || (lower.includes("api key") && lower.includes("not set"))) {
    return {
      title: "This demo isn't available right now",
      message: "We couldn't start this demo. Try another one from the lab, or check back later.",
    };
  }

  if (raw.includes("401") || lower.includes("invalid api key") || lower.includes("authentication")) {
    return {
      title: "This demo isn't available right now",
      message: "We couldn't start this demo. Try another one from the lab, or check back later.",
    };
  }

  if (lower.includes("unknown demo") || lower.includes("demo not found")) {
    return {
      title: "Demo not found",
      message: "That demo doesn't exist. Head back to the lab and pick another one.",
    };
  }

  if (lower.includes("upload") && lower.includes("first")) {
    return {
      title: "Upload a file first",
      message: "Add a document, then ask your question.",
    };
  }

  if (lower.includes("timeout") || lower.includes("timed out")) {
    return {
      title: "That took too long",
      message: "The demo didn't finish in time. Try a shorter question and run it again.",
    };
  }

  if (
    lower.includes("jsondecodeerror") ||
    (lower.includes("expecting") && lower.includes("delimiter")) ||
    lower.includes("no json object found")
  ) {
    return parseError();
  }

  if (!looksTechnical(raw)) {
    return {
      title: title || "Something went wrong",
      message: raw,
    };
  }

  return {
    title: "Something went wrong",
    message: "We couldn't complete your request. Please try again in a moment.",
  };
}

export function formatErrorDisplay(err: FriendlyError): string {
  return `${err.title}\n\n${err.message}`;
}
