"""HTTP SSE smoke tests against a running API."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import httpx

from api.diagnostics.cases import DEMO_CASES, DemoCase
from api.diagnostics.runner_util import evaluate_case, iter_live_cases, summarize_events


def parse_sse(body: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for chunk in body.split("\n\n"):
        line = next((l for l in chunk.split("\n") if l.startswith("data: ")), None)
        if not line:
            continue
        try:
            events.append(json.loads(line[6:]))
        except json.JSONDecodeError:
            continue
    return events


def post_case(base: str, case: DemoCase, timeout: float) -> tuple[list[dict[str, Any]], str]:
    url = f"{base.rstrip('/')}/demos/{case.slug}/run"
    data: dict[str, str] = {}
    files: list[tuple[str, tuple[str, bytes, str]]] = []

    for key, value in case.payload.items():
        if key in {"file_path", "file_paths"}:
            continue
        if value is None:
            continue
        data[key] = str(value)

    file_path = case.payload.get("file_path")
    if file_path:
        path = Path(str(file_path))
        if path.is_file():
            mime = "application/octet-stream"
            if path.suffix.lower() == ".pdf":
                mime = "application/pdf"
            elif path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
                mime = "image/png"
            elif path.suffix.lower() == ".wav":
                mime = "audio/wav"
            elif path.suffix.lower() == ".txt":
                mime = "text/plain"
            files.append(("files", (path.name, path.read_bytes(), mime)))

    with httpx.Client(timeout=timeout) as client:
        response = client.post(url, data=data, files=files or None)
        if response.status_code != 200:
            return [], f"HTTP {response.status_code}: {response.text[:200]}"
        return parse_sse(response.text), ""


def run_smoke(
    base: str,
    *,
    include_slow: bool = False,
    slugs: set[str] | None = None,
    timeout: float = 180.0,
) -> list[tuple[DemoCase, bool, str]]:
    outcomes: list[tuple[DemoCase, bool, str]] = []
    for case in iter_live_cases(DEMO_CASES, include_slow=include_slow):
        if slugs and case.slug not in slugs:
            continue
        if case.skip_live_reason and not include_slow:
            outcomes.append((case, False, f"skipped: {case.skip_live_reason}"))
            continue
        try:
            events, err = post_case(base, case, timeout)
            if err:
                outcomes.append((case, False, err))
                continue
            ok, detail = evaluate_case(case, events)
            if not ok:
                summary = summarize_events(events)
                detail = f"{detail}; types={summary['types']}"
            outcomes.append((case, ok, detail))
        except Exception as exc:
            outcomes.append((case, False, f"{type(exc).__name__}: {exc}"))
    return outcomes


def print_outcomes(outcomes: list[tuple[DemoCase, bool, str]], as_json: bool = False) -> int:
    if as_json:
        payload = [
            {"case_id": c.case_id, "slug": c.slug, "ok": ok, "detail": detail}
            for c, ok, detail in outcomes
        ]
        print(json.dumps(payload, indent=2))
    else:
        for case, ok, detail in outcomes:
            mark = "OK" if ok else "FAIL"
            if detail.startswith("skipped:"):
                mark = "SKIP"
            print(f"[{mark:<4}] {case.case_id:<22} {detail}")
    failed = sum(1 for _, ok, d in outcomes if not ok and not d.startswith("skipped:"))
    skipped = sum(1 for _, _, d in outcomes if d.startswith("skipped:"))
    passed = sum(1 for _, ok, d in outcomes if ok)
    print(f"\n{passed} passed, {failed} failed, {skipped} skipped")
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI Lab HTTP smoke tests")
    parser.add_argument("--base", default="http://127.0.0.1:8080", help="API base URL")
    parser.add_argument("--include-slow", action="store_true", help="Run slow demos")
    parser.add_argument("--slug", action="append", help="Limit to slug (repeatable)")
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    slugs = set(args.slug) if args.slug else None
    outcomes = run_smoke(
        args.base,
        include_slow=args.include_slow,
        slugs=slugs,
        timeout=args.timeout,
    )
    return print_outcomes(outcomes, as_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
