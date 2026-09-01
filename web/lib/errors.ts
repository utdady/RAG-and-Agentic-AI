export type FriendlyError = {
  title: string;
  message: string;
};

function waitHint(raw: string): string {
  const minMatch = raw.match(/try again in (\d+(?:\.\d+)?)\s*m/i);
  if (minMatch) {
    const minutes = Math.max(1, Math.round(Number(minMatch[1])));
    return ` Please try again in about ${minutes} minute${minutes === 1 ? "" : "s"}.`;
  }
  const secMatch = raw.match(/try again in (\d+(?:\.\d+)?)\s*s/i);
  if (secMatch) {
    const seconds = Math.max(5, Math.round(Number(secMatch[1])));
    if (seconds >= 60) {
      const minutes = Math.max(1, Math.round(seconds / 60));
      return ` Please try again in about ${minutes} minute${minutes === 1 ? "" : "s"}.`;
    }
    return ` Please try again in about ${seconds} seconds.`;
  }
  return " Please try again in a few minutes.";
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
    if (lower.includes("tokens per day") || lower.includes("tpd") || lower.includes("per day")) {
      return {
        title: "Daily usage limit reached",
        message:
          "This demo has used its allowed tokens for today." +
          waitHint(raw) +
          " You can also come back tomorrow.",
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
