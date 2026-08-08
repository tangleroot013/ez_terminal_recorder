# Absolute dir of this file, captured at source time (zsh-safe, no BASH_SOURCE)
REC2MD_SCRIPT_DIR="${${(%):-%x}:A:h}"

rec2md() {
  emulate -L zsh
  local title="${1:-session-$(date +%Y%m%d-%H%M%S)}"
  local outdir="${REC2MD_DIR:-$HOME/recordings}"
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
