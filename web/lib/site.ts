/** Site-wide URLs from env (safe for client components). */

const portfolioFromEnv = process.env.NEXT_PUBLIC_PORTFOLIO_URL?.trim();

/** Prefer env, but ignore the retired GitHub Pages URL if it is still set on Vercel. */
export const PORTFOLIO_URL =
  portfolioFromEnv && !portfolioFromEnv.includes("utdady.github.io")
    ? portfolioFromEnv.replace(/\/$/, "")
    : "https://aditya-bhaskar.vercel.app";

export const GITHUB_REPO =
  "https://github.com/utdady/RAG-and-Agentic-AI";

export function isLocalHost(hostname: string) {
  return (
    hostname === "localhost" ||
    hostname === "127.0.0.1" ||
    hostname === "[::1]"
  );
}
