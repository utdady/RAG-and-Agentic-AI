import Link from "next/link";
import { PORTFOLIO_URL } from "@/lib/site";

export function PortfolioLink({
  className,
  onNavigate,
}: {
  className?: string;
  onNavigate?: () => void;
}) {
  return (
    <Link
      href={PORTFOLIO_URL}
      onClick={onNavigate}
      className={
        className ??
        "text-sm text-[var(--txt2)] transition hover:text-accent"
      }
    >
      ← Portfolio
    </Link>
  );
}
