"""Preflight checks for the AI Lab hub (no LLM calls)."""

from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from api.adapters.dispatch import RUNNERS
from api.bootstrap import REPO, groq_ready
from api.catalog import DEMOS
from api.diagnostics.cases import DEMO_CASES, FIXTURES, SLUG_APP_FOLDERS
from api.diagnostics.runner_util import collect_events, evaluate_case
from api.fixtures.generate import ensure_fixtures
from shared.llm import resolve_groq_model


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str = ""


def web_slugs() -> set[str]:
    ts = REPO / "web" / "lib" / "demos.ts"
    if not ts.is_file():
        return set()
    text = ts.read_text(encoding="utf-8")
    return set(re.findall(r'slug:\s*"([^"]+)"', text))


def check_catalog_sync() -> CheckResult:
    api_slugs = {d["slug"] for d in DEMOS}
    ui = web_slugs()
    if not ui:
        return CheckResult("catalog-sync", False, "web/lib/demos.ts not found")
    missing_ui = sorted(api_slugs - ui)
    missing_api = sorted(ui - api_slugs)
    if missing_ui or missing_api:
        parts = []
        if missing_ui:
            parts.append(f"api only: {missing_ui}")
        if missing_api:
            parts.append(f"web only: {missing_api}")
        return CheckResult("catalog-sync", False, "; ".join(parts))
    return CheckResult("catalog-sync", True, f"{len(api_slugs)} slugs match")


def check_groq_env() -> CheckResult:
    if not groq_ready():
        return CheckResult("groq-key", False, "GROQ_API_KEY not set")
    model = resolve_groq_model()
    return CheckResult("groq-model", True, model)


def check_runners_registered() -> CheckResult:
    catalog = {d["slug"] for d in DEMOS}
    runners = set(RUNNERS)
    missing = sorted(catalog - runners)
    extra = sorted(runners - catalog)
    if missing:
        return CheckResult("runners", False, f"missing adapters: {missing}")
    if extra:
        return CheckResult("runners", True, f"ok (+ extra: {extra})")
    return CheckResult("runners", True, f"{len(runners)} runners")


def check_app_folders() -> list[CheckResult]:
    results: list[CheckResult] = []
    for slug, folder in SLUG_APP_FOLDERS.items():
        path = REPO / folder
        ok = path.is_dir()
        results.append(
            CheckResult(f"app:{slug}", ok, str(path) if ok else f"missing folder {folder}")
        )
    return results


def check_fixtures() -> list[CheckResult]:
    ensure_fixtures()
    needed = sorted({c.fixture for c in DEMO_CASES if c.fixture})
    results: list[CheckResult] = []
    for name in needed:
        path = FIXTURES / name
        results.append(
            CheckResult(
                f"fixture:{name}",
                path.is_file(),
                str(path) if path.is_file() else "missing",
            )
        )
    return results


def check_import(slug: str) -> CheckResult:
    runner = RUNNERS.get(slug)
    if runner is None:
        return CheckResult(f"import:{slug}", False, "no runner")
    mod = runner.__module__
    try:
        importlib.import_module(mod)
        return CheckResult(f"import:{slug}", True, mod)
    except Exception as exc:
        return CheckResult(f"import:{slug}", False, f"{type(exc).__name__}: {exc}")


def check_require_groq_unit() -> CheckResult:
    import api.adapters.common as common

    original = common.groq_ready
    try:
        common.groq_ready = lambda: True
        blocked = common.require_groq()
        if blocked is not None:
            return CheckResult("require-groq-ready", False, "expected None when Groq ready")
        common.groq_ready = lambda: False
        blocked = common.require_groq()
        if not blocked or blocked[0].get("type") != "error":
            return CheckResult("require-groq-missing", False, "expected error list")
        return CheckResult("require-groq", True, "ok")
    finally:
        common.groq_ready = original


def check_unit_cases() -> list[CheckResult]:
    results: list[CheckResult] = []
    for case in DEMO_CASES:
        if case.live:
            continue
        try:
            events = collect_events(case.slug, case.payload)
            ok, detail = evaluate_case(case, events)
            results.append(CheckResult(f"unit:{case.case_id}", ok, detail))
        except Exception as exc:
            results.append(
                CheckResult(f"unit:{case.case_id}", False, f"{type(exc).__name__}: {exc}")
            )
    return results


def probe_adapter(case: DemoCase) -> CheckResult:
    try:
        events = collect_events(case.slug, case.payload)
        ok, detail = evaluate_case(case, events)
        return CheckResult(f"probe:{case.case_id}", ok, detail)
    except ModuleNotFoundError as exc:
        return CheckResult(f"probe:{case.case_id}", False, f"ModuleNotFoundError: {exc.name}")
    except Exception as exc:
        return CheckResult(f"probe:{case.case_id}", False, f"{type(exc).__name__}: {exc}")


def run_preflight(
    *,
    include_imports: bool = True,
    probe: bool = False,
    include_slow: bool = False,
) -> list[CheckResult]:
    results: list[CheckResult] = [
        check_catalog_sync(),
        check_groq_env(),
        check_runners_registered(),
        check_require_groq_unit(),
    ]
    results.extend(check_app_folders())
    results.extend(check_fixtures())
    results.extend(check_unit_cases())
    if include_imports:
        for slug in sorted(SLUG_APP_FOLDERS):
            results.append(check_import(slug))
    if probe:
        from api.diagnostics.runner_util import iter_live_cases

        for case in iter_live_cases(DEMO_CASES, include_slow=include_slow):
            if case.skip_live_reason and not include_slow:
                continue
            results.append(probe_adapter(case))
    return results


def print_results(results: list[CheckResult], as_json: bool = False) -> int:
    if as_json:
        print(json.dumps([r.__dict__ for r in results], indent=2))
    else:
        width = max(len(r.name) for r in results) if results else 10
        for r in results:
            mark = "OK" if r.ok else "FAIL"
            detail = f" — {r.detail}" if r.detail else ""
            print(f"[{mark:<4}] {r.name:<{width}}{detail}")
    failed = sum(1 for r in results if not r.ok)
    print(f"\n{len(results) - failed}/{len(results)} passed")
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI Lab preflight checks")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument(
        "--skip-imports",
        action="store_true",
        help="Skip per-adapter import checks (faster)",
    )
    parser.add_argument(
        "--probe",
        action="store_true",
        help="Run one adapter smoke per demo (needs Groq; catches missing deps)",
    )
    parser.add_argument(
        "--include-slow",
        action="store_true",
        help="Include slow demos in --probe",
    )
    args = parser.parse_args(argv)
    results = run_preflight(
        include_imports=not args.skip_imports,
        probe=args.probe,
        include_slow=args.include_slow,
    )
    return print_results(results, as_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
