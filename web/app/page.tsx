import Link from "next/link";
import { HubShell } from "@/components/HubShell";
import { PortfolioLink } from "@/components/PortfolioLink";
import {
  DEMO_GROUPS,
  DEMOS,
  FEATURED_SLUGS,
  demoBySlug,
  isFeaturedSlug,
} from "@/lib/demos";
import { GITHUB_REPO } from "@/lib/site";

function TagPill({ label, small }: { label: string; small?: boolean }) {
  return (
    <span
      className={`font-mono text-[var(--txt2)] border border-[var(--line-hover)] rounded-full ${
        small ? "text-[10.5px] px-[7px] py-0.5" : "text-[11px] px-2 py-[3px]"
      }`}
    >
      {label}
    </span>
  );
}

export default function HomePage() {
  const demoCount = DEMOS.length;
  const featured = FEATURED_SLUGS.map((slug) => demoBySlug(slug)).filter(
    Boolean,
  );

  return (
    <HubShell>
      <div className="mx-auto w-full max-w-[1200px] px-6 py-10 text-left sm:px-8 lg:px-12 lg:py-14">
        <nav className="mb-12 flex items-center justify-between font-mono text-[13px] text-[var(--txt2)]">
          <span className="tracking-[0.04em] text-[var(--txt)]">AI LAB</span>
          <div className="flex items-center gap-5">
            <PortfolioLink className="text-[13px] text-[var(--txt2)] transition hover:text-accent" />
            <a
              href={GITHUB_REPO}
              target="_blank"
              rel="noopener noreferrer"
              className="transition hover:text-accent"
            >
              GitHub ↗
            </a>
          </div>
        </nav>

        <p className="mb-3.5 font-mono text-[13px] tracking-[0.02em] text-accent">
          Live demos
        </p>
        <h1 className="font-display mb-5 text-[34px] leading-[1.05] font-extrabold tracking-[-0.01em] sm:text-[46px]">
          Retrieval, agents, and reasoning
          <br className="hidden sm:block" /> you can actually run.
        </h1>
        <p className="mb-10 max-w-[560px] text-base leading-relaxed text-[var(--txt2)]">
          {demoCount} FastAPI-backed apps from one monorepo — RAG pipelines,
          multi-agent crews, vision, and audio. Pick a demo below to open its
          workspace.
        </p>

        <div className="mb-14 flex items-center gap-2 border-b border-[var(--line)] pb-8 font-mono text-[12.5px] text-[var(--txt3)]">
          <span
            className="inline-block h-1.5 w-1.5 shrink-0 rounded-full bg-[var(--live)] shadow-[0_0_8px_var(--live)]"
            aria-hidden
          />
          Demos wake from idle on first request — expect ~10–15s on cold start
        </div>

        <div className="mb-4 flex flex-wrap items-baseline gap-2.5 font-mono text-[13px] text-[var(--txt2)]">
          <span>Start here</span>
          <span className="text-[var(--txt3)]">
            — strongest picks for a quick read
          </span>
        </div>
        <div className="mb-16 grid gap-4 md:grid-cols-3">
          {featured.map((demo) => {
            if (!demo?.featured) return null;
            const tags = demo.featured.tags ?? demo.tags;
            return (
              <Link
                key={demo.slug}
                href={`/demos/${demo.slug}`}
                className="group relative overflow-hidden rounded-[10px] border border-[var(--line)] bg-[linear-gradient(160deg,var(--bg2),var(--surface))] px-6 pt-6 pb-5 transition duration-200 hover:-translate-y-0.5 hover:border-accent focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
              >
                <span
                  className="pointer-events-none absolute inset-x-0 top-0 h-0.5 bg-[linear-gradient(90deg,var(--accent),transparent)] opacity-70"
                  aria-hidden
                />
                <span className="mb-3.5 inline-block rounded bg-[var(--accent-dim)] px-2 py-[3px] font-mono text-[10.5px] text-accent">
                  FEATURED
                </span>
                <h3 className="font-display mb-2 text-[19px] font-bold">
                  {demo.title}
                </h3>
                <p className="mb-4 text-[13.5px] leading-normal text-[var(--txt2)]">
                  {demo.featured.blurb}
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {tags.map((tag) => (
                    <TagPill key={tag} label={tag} />
                  ))}
                </div>
              </Link>
            );
          })}
        </div>

        <div className="space-y-11">
          {DEMO_GROUPS.map((group) => {
            const slugs = group.slugs.filter((slug) => !isFeaturedSlug(slug));
            if (slugs.length === 0) return null;
            return (
              <section key={group.id}>
                <div className="mb-4 flex items-baseline gap-2.5 font-mono text-[13px] text-[var(--txt2)]">
                  <span>{group.label}</span>
                  <span className="text-[var(--txt3)]">{slugs.length}</span>
                </div>
                <div className="grid gap-3.5 sm:grid-cols-2">
                  {slugs.map((slug) => {
                    const demo = demoBySlug(slug);
                    if (!demo) return null;
                    return (
                      <Link
                        key={slug}
                        href={`/demos/${slug}`}
                        className="rounded-[10px] border border-[var(--line)] bg-[var(--surface)] px-[22px] py-5 text-left transition hover:border-[var(--line-hover)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
                      >
                        <h3 className="font-display mb-1.5 text-base font-bold">
                          {demo.title}
                        </h3>
                        <p className="mb-3.5 text-[13px] leading-normal text-[var(--txt2)]">
                          {demo.tagline}
                        </p>
                        <div className="flex flex-wrap gap-1.5">
                          {demo.tags.map((tag) => (
                            <TagPill key={tag} label={tag} small />
                          ))}
                        </div>
                      </Link>
                    );
                  })}
                </div>
              </section>
            );
          })}
        </div>
      </div>
    </HubShell>
  );
}
