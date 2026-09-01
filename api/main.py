from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.bootstrap import groq_ready
from api.catalog import DEMOS
from api.routers.demos import router as demos_router

app = FastAPI(title="AI Lab Demo Hub API", version="0.1.0")

# Bumped when hub behavior changes; start_lab checks this after restart.
HUB_REVISION = "vision-qwen-1"

origins = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,https://utdady.github.io,https://www.utdady.github.io",
    ).split(",")
    if o.strip()
]
# Allow any Vercel preview / production hub
origins.append("https://*.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(demos_router)


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "groq": groq_ready(),
        "llm_provider": os.getenv("LLM_PROVIDER", "groq"),
        "demos": len(DEMOS),
        "revision": HUB_REVISION,
    }
