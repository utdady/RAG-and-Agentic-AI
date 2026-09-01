import Link from "next/link";

function ChevronLeft({ className }: { className?: string }) {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      aria-hidden
      className={className}
    >
      <path
        d="M10 3L5 8l5 5"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function BackToLab({
  className,
  label = "Back to lab",
}: {
  className?: string;
  label?: string;
}) {
  return (
    <Link
      href="/"
      className={`inline-flex items-center gap-1.5 text-sm text-[var(--txt2)] transition hover:text-accent ${className ?? ""}`}
    >
      <ChevronLeft />
      {label}
    </Link>
  );
}

export function BackToLabButton({
  className,
  label = "Back to lab",
}: {
  className?: string;
  label?: string;
}) {
  return (
    <Link
      href="/"
      aria-label={label}
      className={`inline-flex items-center justify-center rounded-lg p-2 text-[var(--txt2)] transition hover:bg-[var(--surface)] hover:text-accent ${className ?? ""}`}
    >
      <ChevronLeft />
    </Link>
  );
}
