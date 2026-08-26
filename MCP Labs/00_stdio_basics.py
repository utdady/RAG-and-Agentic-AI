"""00 — stdout vs stderr (course notebook warm-up; no MCP)."""

from __future__ import annotations

import sys

from _bootstrap import banner


def main() -> None:
    banner("00 — stdout / stderr basics")

    my_code = "hello"
    print(f"my_code={my_code}")
    sys.stdout.write("Hello via stdout.write\n")

    print("This is standard output (stdout)")
    print("This is an error message (stderr)", file=sys.stderr)

    try:
        _ = 10 / 0
    except ZeroDivisionError as e:
        print(f"Error occurred: {e}", file=sys.stderr)

    print("Done. (Course also demoed input()/sys.exit — skipped here.)")


if __name__ == "__main__":
    main()
