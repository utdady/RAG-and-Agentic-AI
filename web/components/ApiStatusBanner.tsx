"use client";

import { useEffect, useState } from "react";
import { isLocalHost } from "@/lib/site";
import { checkApiHealth } from "@/lib/sse";

export function ApiStatusBanner() {
  const [ok, setOk] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      const healthy = await checkApiHealth();
      if (!cancelled) setOk(healthy);
    }

    poll();
    const id = window.setInterval(poll, 8000);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, []);

  if (ok !== false) return null;

  const local = isLocalHost(window.location.hostname);

  return (
    <div className="border-b border-[var(--warn)]/40 bg-[var(--warn)]/10 px-4 py-2 text-center text-sm text-[var(--warn)]">
      {local ? (
        <>
          API offline — from repo root run{" "}
          <code className="rounded bg-black/30 px-1.5 py-0.5 font-mono text-xs">
            .\scripts\start_lab.ps1
          </code>{" "}
          and keep both windows open. Then hard-refresh (
          <kbd className="font-mono text-xs">Ctrl+Shift+R</kbd>).
        </>
      ) : (
        <>
          API offline — live demos are temporarily unavailable. Check{" "}
          <code className="rounded bg-black/30 px-1.5 py-0.5 font-mono text-xs">
            NEXT_PUBLIC_API_URL
          </code>{" "}
          on Vercel and Railway <code className="font-mono text-xs">/health</code>.
        </>
      )}
    </div>
  );
}
