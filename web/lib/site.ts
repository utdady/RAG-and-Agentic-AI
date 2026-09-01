/** Site-wide URLs from env (safe for client components). */

export const PORTFOLIO_URL =
  process.env.NEXT_PUBLIC_PORTFOLIO_URL ?? "https://utdady.github.io";

export const GITHUB_REPO =
  "https://github.com/utdady/RAG-and-Agentic-AI";

export function isLocalHost(hostname: string) {
  return (
    hostname === "localhost" ||
    hostname === "127.0.0.1" ||
    hostname === "[::1]"
  );
}
