#!/usr/bin/env python3
"""Convert an asciinema v2 .cast recording into a markdown transcript."""
import sys
import json
import re
import datetime

ANSI_RE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


def strip_ansi(s: str) -> str:
    return ANSI_RE.sub('', s)


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: rec2md.py <in.cast> <out.md> <title>", file=sys.stderr)
        return 1

    cast_path, md_path, title = sys.argv[1], sys.argv[2], sys.argv[3]

    with open(cast_path, "r", encoding="utf-8") as f:
        lines = [ln for ln in f.read().splitlines() if ln.strip()]

    if not lines:
        print("[error] empty cast file", file=sys.stderr)
        return 1

    header = json.loads(lines[0])
    duration = 0.0
    chunks = []
    for ln in lines[1:]:
        try:
            t, kind, data = json.loads(ln)
        except (ValueError, json.JSONDecodeError):
            continue
        if kind == "o":
            chunks.append(data)
        duration = max(duration, t)

    transcript = strip_ansi("".join(chunks))
    recorded_at = header.get("timestamp")
    when = (
        datetime.datetime.fromtimestamp(recorded_at, tz=datetime.timezone.utc).isoformat()
        if recorded_at else "unknown"
    )

    body = (
        f"# {title}\n\n"
        f"- recorded: {when}\n"
        f"- duration: {duration:.1f}s\n"
        f"- source cast: `{cast_path}`\n\n"
        "```term\n"
        f"{transcript}\n"
        "```\n"
    )

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(body)

    print(f"[ok] wrote {md_path} ({len(transcript)} chars, {duration:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
