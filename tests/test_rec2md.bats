#!/usr/bin/env bats

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
