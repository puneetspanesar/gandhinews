#!/bin/bash
# Publish (RUNBOOK.md section E) in one command, after the gate and apply_verdict:
#   bash newsroom/scripts/publish.sh <run-name> "<one-line summary>"
# Needs /home/claude/gn-work/commit.txt (the commit message, ending with the attribution lines).
# Writes the run record, commits, takes the lock only for the pull-build-push, re-applies this run's homepage picks
# when the pull merged another run's work, builds with the full build gate, pushes, releases the lock, then waits
# until the live site runs the pushed commit. Exit 0 live, 1 not pushed (fix and run again), 4 pushed but not live yet.
cd /home/claude/gandhinews || exit 1
RUN=${1:?usage: publish.sh <run-name> "<summary>"}; SUM=${2:-}
W=${GN_WORK:-/home/claude/gn-work/}
[ -s "$W/commit.txt" ] || { echo "write $W/commit.txt first"; exit 1; }
python3 newsroom/scripts/run_record.py write "$RUN" "$SUM" || exit 1
git add -A content public/photos newsroom scripts src && git commit -q -F "$W/commit.txt" || echo "(nothing new to commit)"
bash newsroom/scripts/lock.sh wait "$RUN" 15 10; lk=$?
[ $lk -eq 0 ] || echo "lock not free after 15 minutes (exit $lk): publishing anyway; the pull and merge below keep both runs' work"
before=$(git rev-parse HEAD)
git pull -q --no-edit origin main || { echo "pull failed: resolve the merge, then run publish.sh again"; bash newsroom/scripts/lock.sh release "$RUN"; exit 1; }
if [ "$(git rev-parse HEAD)" != "$before" ]; then
  echo "merged newer work from main: re-applying this run's homepage picks"
  python3 newsroom/scripts/refresh_home.py $(cat "$W/home_args" 2>/dev/null) >/dev/null
  python3 newsroom/scripts/check_fresh.py; rc=$?
  [ $rc -eq 1 ] && { echo "check_fresh fails after the merge: fix homepage.json, then run publish.sh again"; bash newsroom/scripts/lock.sh release "$RUN"; exit 1; }
  git add content/homepage.json && git commit -q -m "Homepage re-applied after merging main" -m "$(tail -3 "$W/commit.txt")" 2>/dev/null
fi
npm run -s build > "$W/build.log" 2>&1; b=$?
if [ $b -ne 0 ]; then echo "full build failed (not pushed):"; tail -25 "$W/build.log"; bash newsroom/scripts/lock.sh release "$RUN"; exit 1; fi
tail -1 "$W/build.log"
git push -q origin HEAD:main || { echo "push rejected: run publish.sh again"; bash newsroom/scripts/lock.sh release "$RUN"; exit 1; }
bash newsroom/scripts/lock.sh release "$RUN"
echo "pushed $(git rev-parse --short HEAD); waiting for the live site"
python3 newsroom/scripts/verify_live.py --expect HEAD && exit 0
exit 4
