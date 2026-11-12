#!/bin/bash
# First command of every stall check (owner, November 12). GitHub starts only a few of the rotation job's scheduled
# runs, so the stall check starts it itself: the job rotates the headlines without AI and does nothing in an hour whose
# homepage has already changed. Then the live check runs on the result.
#   bash /home/claude/gandhinews/newsroom/scripts/stall_first.sh      ends with verify_live.py's "OK at" or LIVE SITE PROBLEMS
cd /home/claude/gandhinews || exit 1
R=repos/puneetspanesar/gandhinews/actions/workflows/home-rotate.yml
before=$(gh api "$R/runs?per_page=1" --jq '.workflow_runs[0].id' 2>/dev/null)
if gh api -X POST "$R/dispatches" -f ref=main >/dev/null 2>&1; then
  for i in $(seq 1 30); do   # up to 5 minutes: the job takes about one
    sleep 10
    read -r id st < <(gh api "$R/runs?per_page=1" --jq '.workflow_runs[0]|"\(.id) \(.status)"' 2>/dev/null)
    [ "$id" != "$before" ] && [ "$st" = completed ] && break
  done
  echo "rotation job: $(gh api "$R/runs?per_page=1" --jq '.workflow_runs[0]|"\(.status) \(.conclusion)"' 2>/dev/null)"
else
  echo "rotation job: could not be started from here (the fix step rotates by hand if the check below asks for it)"
fi
git pull -q --rebase origin main 2>/dev/null
python3 newsroom/scripts/verify_live.py
