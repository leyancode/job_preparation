#!/usr/bin/env bash
set -euo pipefail

demo_without_dev_null() {
  echo "== Without < /dev/null =="
  printf '%s\n' small medium large very-large |
  while read -r scale; do
    echo "outer loop got: ${scale}"

    # This simulates a command inside the loop that reads stdin.
    # It consumes one extra line from the same input stream as the loop.
    read -r stolen || true
    echo "inner command stole: ${stolen:-<nothing>}"
  done
}

demo_with_dev_null() {
  echo "== With < /dev/null =="
  printf '%s\n' small medium large very-large |
  while read -r scale; do
    echo "outer loop got: ${scale}"

    # Now the inner command reads from an empty input source instead.
    # It cannot consume the loop's remaining lines.
    read -r stolen < /dev/null || true
    echo "inner command stole: ${stolen:-<nothing>}"
  done
}

demo_without_dev_null
echo
demo_with_dev_null
