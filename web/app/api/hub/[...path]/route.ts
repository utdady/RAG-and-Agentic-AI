import type { NextRequest } from "next/server";

const API = process.env.API_PROXY_URL ?? "http://127.0.0.1:8080";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
/** Long CrewAI / vision demos need more than the default serverless limit. */
export const maxDuration = 300;

async function proxy(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> },
) {
  const { path } = await ctx.params;
  const target = `${API}/${path.join("/")}${req.nextUrl.search}`;

  const headers = new Headers();
  const contentType = req.headers.get("content-type");
  if (contentType) headers.set("content-type", contentType);

  const init: RequestInit & { duplex?: "half" } = {
    method: req.method,
    headers,
    body:
      req.method === "GET" || req.method === "HEAD" ? undefined : req.body,
    duplex: "half",
  };

  let upstream: Response;
  try {
    upstream = await fetch(target, init);
  } catch {
    return Response.json(
      { ok: false, error: "FastAPI backend unreachable at " + API },
      { status: 502 },
    );
  }

  return new Response(upstream.body, {
    status: upstream.status,
    headers: {
      "Content-Type":
        upstream.headers.get("content-type") || "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
      "X-Accel-Buffering": "no",
    },
  });
}

export const GET = proxy;
export const POST = proxy;
