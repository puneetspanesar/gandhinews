#!/bin/bash
# The gate (RUNBOOK.md section D), every check in order, in one command. Run from anywhere.
#   bash newsroom/scripts/gate.sh          exit 0 all pass | 2 pass with recorded rule breaches | 1 something to fix
# It prints one line per check and, for failures, the check's own output. Nothing is piped away: every check's exit
# code is read. Uses the fast build (no link and gate checks) plus check-links and gate.mjs run separately, so the
# whole gate takes one build.
cd /home/claude/gandhinews || exit 1
W=${GN_WORK:-/home/claude/gn-work/}; mkdir -p "$W"; rm -f "$W/breaches.txt"
fail=0; soft=0
step() { local name=$1; shift; local out; out=$("$@" 2>&1); local rc=$?
  if [ $rc -eq 0 ]; then echo "OK    $name"
  elif [ $rc -eq 2 ] && [ "$name" = "check_fresh" ]; then echo "BREACH $name"; echo "$out" | sed 's/^/      /'; soft=1
  else echo "FAIL  $name (exit $rc)"; echo "$out" | tail -40 | sed 's/^/      /'; fail=1; fi; }
changed=$(git diff --name-only --diff-filter=AMR origin/main -- content/en | grep '\.md$')
[ -n "$changed" ] && python3 newsroom/scripts/fix_dates.py $changed >/dev/null
step check_fresh python3 newsroom/scripts/check_fresh.py
step check_photos npm run -s check:photos
step build npm run -s build:fast
if [ $fail -eq 0 ]; then
  step check_links node scripts/check-links.mjs
  step build_gate node scripts/gate.mjs
  step audit python3 newsroom/scripts/audit.py --changed
  step layout node newsroom/scripts/check_layout.cjs
fi
[ $fail -eq 1 ] && { echo "GATE: FAIL"; exit 1; }
[ $soft -eq 1 ] && { echo "GATE: PASS WITH BREACHES (recorded in the run record)"; exit 2; }
echo "GATE: PASS"; exit 0
