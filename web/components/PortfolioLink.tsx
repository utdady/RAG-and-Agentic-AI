import { PORTFOLIO_URL } from "@/lib/site";

export function PortfolioLink({
  className,
  onNavigate,
}: {
  className?: string;
  onNavigate?: () => void;
}) {
  return (
    <a
      href={PORTFOLIO_URL}
      onClick={onNavigate}
      className={
        className ??
        "text-sm text-[var(--txt2)] transition hover:text-accent"
      }
    >
      ← Portfolio
    </a>
  );
}
