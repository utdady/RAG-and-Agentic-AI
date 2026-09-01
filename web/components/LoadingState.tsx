export function PixelLoader({
  label,
  elapsed,
  thinking = false,
}: {
  label?: string;
  elapsed?: string;
  thinking?: boolean;
}) {
  return (
    <div className="flex items-center gap-4">
      <div className="pixel-loader" aria-hidden>
        {Array.from({ length: 16 }).map((_, i) => (
          <span key={i} />
        ))}
      </div>
      <div>
        {thinking ? (
          <div className="text-sm text-[var(--txt2)]" aria-live="polite">
            Thinking
            <span className="thinking-dots" aria-hidden>
              <span>.</span>
              <span>.</span>
              <span>.</span>
            </span>
          </div>
        ) : (
          <div className="font-mono text-xs tracking-widest text-accent uppercase">
            {label || "Churning"}
          </div>
        )}
        {elapsed ? (
          <div className="font-mono text-xs text-[var(--txt2)] mt-1">{elapsed}</div>
        ) : null}
      </div>
    </div>
  );
}

export const LoadingState = PixelLoader;
