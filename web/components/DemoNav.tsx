import Link from "next/link";
import { PortfolioLink } from "@/components/PortfolioLink";
import { DEMO_GROUPS, demoBySlug } from "@/lib/demos";
import { GITHUB_REPO } from "@/lib/site";

export function DemoBrand({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <div className="shrink-0 border-b border-[var(--line)] p-5">
      <Link href="/" className="block" onClick={onNavigate}>
        <div className="font-mono text-[11px] tracking-[0.2em] uppercase text-accent">
          AI Lab
        </div>
        <h1 className="mt-1 text-lg font-semibold">Live demos</h1>
      </Link>
    </div>
  );
}

export function DemoNav({
  active,
  onNavigate,
  className,
}: {
  active?: string;
  onNavigate?: () => void;
  className?: string;
}) {
  return (
    <nav
      className={`flex flex-1 flex-col overflow-y-auto px-3 py-4 ${className ?? ""}`}
    >
      {DEMO_GROUPS.map((group) => (
        <div key={group.id} className="mb-5 last:mb-2">
          <div className="px-3 pb-1.5 font-mono text-[10px] tracking-widest uppercase text-[var(--txt2)]">
            {group.label}
          </div>
          <ul className="space-y-0.5">
            {group.slugs.map((slug) => {
              const demo = demoBySlug(slug);
              if (!demo) return null;
              const isActive = active === slug;
              return (
                <li key={slug}>
                  <Link
                    href={`/demos/${slug}`}
                    onClick={onNavigate}
                    className={`block rounded-lg px-3 py-2 text-sm transition ${
                      isActive
                        ? "bg-[var(--surface)] font-medium text-accent"
                        : "text-[var(--txt2)] hover:bg-[var(--surface)] hover:text-[var(--txt)]"
                    }`}
                  >
                    {demo.title}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      ))}
      <div className="mt-auto border-t border-[var(--line)] px-3 py-4 space-y-2">
        <PortfolioLink
          className="block px-3 py-1.5 text-sm text-[var(--txt2)] transition hover:text-accent"
          onNavigate={onNavigate}
        />
        <a
          href={GITHUB_REPO}
          target="_blank"
          rel="noopener noreferrer"
          onClick={onNavigate}
          className="block px-3 py-1.5 text-sm text-[var(--txt2)] transition hover:text-accent"
        >
          GitHub repo ↗
        </a>
      </div>
    </nav>
  );
}
