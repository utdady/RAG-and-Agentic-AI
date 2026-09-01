"use client";

import Link from "next/link";
import { useEffect, useState, type ReactNode } from "react";
import { ApiStatusBanner } from "@/components/ApiStatusBanner";
import { BackToLabButton } from "@/components/BackToLab";
import { DemoNav } from "@/components/DemoNav";
import { Sidebar } from "@/components/Sidebar";
import { demoBySlug } from "@/lib/demos";

function MenuIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 20 20"
      fill="none"
      aria-hidden
      className="text-[var(--txt)]"
    >
      <path
        d="M3 5h14M3 10h14M3 15h14"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function DemoShell({
  active,
  children,
}: {
  active: string;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const demo = demoBySlug(active);
  const close = () => setOpen(false);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") close();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  return (
    <div className="flex min-h-screen flex-col lg:flex-row">
      <div className="sticky top-0 z-40 flex items-center gap-1 border-b border-[var(--line)] bg-[var(--bg2)] px-3 py-3 lg:hidden">
        <BackToLabButton />
        <button
          type="button"
          onClick={() => setOpen(true)}
          aria-label="Open demo menu"
          aria-expanded={open}
          className="rounded-lg p-2 hover:bg-[var(--surface)]"
        >
          <MenuIcon />
        </button>
        <div className="flex min-w-0 flex-1 items-baseline gap-1.5">
          <Link
            href="/"
            className="shrink-0 font-mono text-xs uppercase tracking-wider leading-none text-accent"
          >
            AI Lab
          </Link>
          <span aria-hidden className="shrink-0 text-xs text-[var(--txt2)]">
            ·
          </span>
          <span className="truncate text-xs font-medium leading-none text-[var(--txt)]">
            {demo?.title ?? "Demo"}
          </span>
        </div>
      </div>

      <button
        type="button"
        aria-label="Close menu"
        onClick={close}
        className={`fixed inset-0 z-50 bg-black/60 transition-opacity duration-300 ease-out lg:hidden ${
          open ? "pointer-events-auto opacity-100" : "pointer-events-none opacity-0"
        }`}
      />
      <aside
        aria-hidden={!open}
        className={`fixed inset-y-0 left-0 z-[60] flex w-72 max-w-[85vw] flex-col border-r border-[var(--line)] bg-[var(--bg2)] transition-transform duration-300 ease-out lg:hidden ${
          open ? "translate-x-0" : "pointer-events-none -translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between border-b border-[var(--line)] p-5">
          <Link
            href="/"
            onClick={close}
            className="font-mono text-[11px] tracking-[0.2em] uppercase text-accent"
          >
            AI Lab
          </Link>
          <button
            type="button"
            onClick={close}
            aria-label="Close menu"
            className="rounded-lg px-2 py-1 text-sm text-[var(--txt2)] hover:bg-[var(--surface)] hover:text-[var(--txt)]"
          >
            Close
          </button>
        </div>
        <DemoNav
          active={active}
          onNavigate={close}
          className="flex min-h-0 flex-1 flex-col"
        />
      </aside>

      <Sidebar active={active} />
      <main className="flex min-h-0 min-w-0 flex-1 flex-col lg:h-screen lg:overflow-hidden">
        <ApiStatusBanner />
        {children}
      </main>
    </div>
  );
}
