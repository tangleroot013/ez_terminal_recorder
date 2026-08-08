#!/usr/bin/env python3
"""
setup_repo.py - ez_terminal_recorder Repository Generator & Scaffolder
"""
import os

FILES = {
    ".gitignore": "*.raw\n*.tmp\n*.cast\n.env\n.DS_Store\n*.swp\n*~\n.idea/\n.vscode/\n",
    ".env.example": 'EZ_TERM_LOG_DIR="${HOME}/obsidian/vault/term_logs"\n',
    "LICENSE": "MIT License\nCopyright (c) 2026 ez_terminal_recorder\n",
    "README.md": "# ez_terminal_recorder\n\nA lightweight Zsh utility for recording terminal sessions.\n",
    "src/rec2md.py": r'''#!/usr/bin/env python3
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
''',
    "src/rec2md.zsh": r'''# Absolute dir of this file, captured at source time (zsh-safe, no BASH_SOURCE)
REC2MD_SCRIPT_DIR="${${(%):-%x}:A:h}"

rec2md() {
  emulate -L zsh
  local title="${1:-session-$(date +%Y%m%d-%H%M%S)}"
  local outdir="${REC2MD_DIR:-${EZ_TERM_LOG_DIR:-$HOME/recordings}}"
  local cast="$outdir/${title}.cast"
  local md="$outdir/${title}.md"

  mkdir -p "$outdir"

  if ! command -v asciinema >/dev/null 2>&1; then
    echo "[error] asciinema not found -- install: pip install --break-system-packages --user asciinema"
    return 1
  fi

  echo "[ok] recording -> $cast  (type 'exit' or Ctrl-D to stop)"
  asciinema rec "$cast" --title "$title" --overwrite || { echo "[error] recording failed"; return 1; }

  if [[ ! -s "$cast" ]]; then
    echo "[error] no cast file produced"
    return 1
  fi

  python3 "$REC2MD_SCRIPT_DIR/rec2md.py" "$cast" "$md" "$title" \
    && echo "[ok] markdown -> $md" \
    || { echo "[error] conversion failed"; return 1; }
}
''',
    "install.sh": r'''#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
TARGET_FILE="$HOME/.zshrc.local"
MARKER_START="# >>> ez_terminal_recorder:rec2md >>>"
MARKER_END="# <<< ez_terminal_recorder:rec2md <<<"

touch "$TARGET_FILE"

if grep -qF "$MARKER_START" "$TARGET_FILE"; then
  echo "[skip] rec2md hook already present in $TARGET_FILE"
else
  {
    echo ""
    echo "$MARKER_START"
    echo "source \"$SCRIPT_DIR/src/rec2md.zsh\""
    echo "$MARKER_END"
  } >> "$TARGET_FILE"
  echo "[ok] rec2md hook installed -> $TARGET_FILE"
fi

echo "[ok] now run: source ~/.zshrc"
''',
    "tests/fixtures/sample.cast": r'''{"version": 2, "width": 80, "height": 24, "timestamp": 1700000000, "env": {"SHELL": "/bin/zsh", "TERM": "xterm-256color"}}
[0.1, "o", "\u001b[32mhello world\u001b[0m\r\n"]
[0.5, "o", "second line\r\n"]
[0.5, "i", "ignored input event\r\n"]
''',
    "tests/test_rec2md.bats": r'''#!/usr/bin/env bats

setup() {
  REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)"
  FIXTURE="$REPO_ROOT/tests/fixtures/sample.cast"
  TMP_MD="$(mktemp -d)/out.md"
}

teardown() {
  rm -f "$TMP_MD"
}

@test "rec2md.py converts a valid cast to markdown" {
  run python3 "$REPO_ROOT/src/rec2md.py" "$FIXTURE" "$TMP_MD" "unit-test-session"
  [ "$status" -eq 0 ]
  [ -f "$TMP_MD" ]
}

@test "output markdown contains the title as a heading" {
  run python3 "$REPO_ROOT/src/rec2md.py" "$FIXTURE" "$TMP_MD" "unit-test-session"
  grep -q "^# unit-test-session" "$TMP_MD"
}

@test "output strips ANSI escape codes and keeps the text" {
  run python3 "$REPO_ROOT/src/rec2md.py" "$FIXTURE" "$TMP_MD" "unit-test-session"
  ! grep -q $'\x1b' "$TMP_MD"
  grep -q "hello world" "$TMP_MD"
}

@test "output includes duration metadata" {
  run python3 "$REPO_ROOT/src/rec2md.py" "$FIXTURE" "$TMP_MD" "unit-test-session"
  grep -q "duration:" "$TMP_MD"
}

@test "input events (kind i) are excluded from transcript" {
  run python3 "$REPO_ROOT/src/rec2md.py" "$FIXTURE" "$TMP_MD" "unit-test-session"
  ! grep -q "ignored input event" "$TMP_MD"
}

@test "fails gracefully on an empty cast file" {
  EMPTY="$(mktemp)"
  run python3 "$REPO_ROOT/src/rec2md.py" "$EMPTY" "$TMP_MD" "empty-test"
  [ "$status" -ne 0 ]
  rm -f "$EMPTY"
}

@test "rejects wrong argument count" {
  run python3 "$REPO_ROOT/src/rec2md.py" "$FIXTURE"
  [ "$status" -ne 0 ]
}
''',
    "tests/run.sh": r'''#!/usr/bin/env bash
set -euo pipefail

if ! command -v bats >/dev/null 2>&1; then
  echo "[error] bats not found -- install: sudo apt install bats  (or: npm install -g bats)"
  exit 1
fi

echo "[ok] running BATS suite"
bats "$(dirname "${BASH_SOURCE[0]}")"/*.bats
'''
}

def main():
    for filepath, content in FILES.items():
        dirname = os.path.dirname(filepath)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        if filepath.endswith((".sh", ".zsh", ".py")):
            os.chmod(filepath, 0o755)
        print(f"Created: {filepath}")
    print("Repository structure generated successfully!")

if __name__ == "__main__":
    main()
