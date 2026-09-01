import Link from "next/link";
import { HubShell } from "@/components/HubShell";
import { PortfolioLink } from "@/components/PortfolioLink";
import { DEMO_GROUPS, demoBySlug } from "@/lib/demos";
import { GITHUB_REPO } from "@/lib/site";

export default function HomePage() {
  return (
    <HubShell>
      <div className="w-full max-w-5xl px-6 py-8 text-left lg:px-12 lg:py-12">
        <header className="border-b border-[var(--line)] pb-8">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <p className="font-mono text-[11px] tracking-[0.2em] uppercase text-accent">
              AI Lab
            </p>
            <div className="flex items-center gap-4">
              <PortfolioLink />
              <a
                href={GITHUB_REPO}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-[var(--txt2)] transition hover:text-accent"
              >
                GitHub ↗
              </a>
            </div>
          </div>
          <h1 className="mt-2 text-4xl font-semibold tracking-tight">Live demos</h1>
          <p className="mt-4 max-w-2xl text-[var(--txt2)]">
            RAG pipelines, agents, vision, and crew workflows from the monorepo.
            Choose a demo below to open its workspace.
          </p>
        </header>

        <div className="mt-10 space-y-10">
          {DEMO_GROUPS.map((group) => (
            <section key={group.id}>
              <h2 className="font-mono text-[11px] tracking-widest uppercase text-[var(--txt2)]">
                {group.label}
              </h2>
              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                {group.slugs.map((slug) => {
                  const demo = demoBySlug(slug);
                  if (!demo) return null;
                  return (
                    <Link
                      key={slug}
                      href={`/demos/${slug}`}
                      className="rounded-2xl border border-[var(--line)] bg-[var(--surface)] p-5 text-left transition hover:border-accent"
                    >
                      <h3 className="text-lg font-medium">{demo.title}</h3>
                      <p className="mt-2 text-sm text-[var(--txt2)]">
                        {demo.tagline}
                      </p>
                    </Link>
                  );
                })}
              </div>
            </section>
          ))}
        </div>
      </div>
    </HubShell>
  );
}
