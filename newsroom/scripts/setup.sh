#!/bin/bash
# Every run starts with: source newsroom/scripts/setup.sh <run-name>    (run-name: hourly-HH, longform-m, longform-e, stall-HH)
# Clones or updates the repo, installs, configures git (Claude as author, main-only fetch, JSON merge driver),
# copies briefs and scripts to the work folder, records the start time. Fails loudly instead of half-working.
set -e
RUN=${1:?usage: source newsroom/scripts/setup.sh <run-name>}
export GN_ROOT=/home/claude/gandhinews/ GN_WORK=/home/claude/gn-work/ TZ=Asia/Kolkata
[ -d /home/claude/gandhinews/.git ] || gh repo clone puneetspanesar/gandhinews /home/claude/gandhinews
cd /home/claude/gandhinews
git config user.name Claude; git config user.email noreply@anthropic.com
git config remote.origin.fetch '+refs/heads/main:refs/remotes/origin/main'
git config merge.gnjson.driver "python3 newsroom/scripts/merge_json.py %O %A %B %P"
git config pull.rebase false
git pull -q origin main
npm ci --silent
mkdir -p "$GN_WORK" && cp newsroom/briefs/*.md newsroom/scripts/*.py newsroom/scripts/blocklist.txt "$GN_WORK"
[ -x /tmp/claude-0/cvenv/bin/python ] || (python3 -m venv /tmp/claude-0/cvenv && /tmp/claude-0/cvenv/bin/pip -q install "opencv-python-headless<5" pillow numpy pyyaml)
python3 -c "import rembg, cairosvg, yaml, PIL" 2>/dev/null || pip install --break-system-packages -q "rembg[cpu]" "opencv-python-headless<5" cairosvg pyyaml pillow
: > "$GN_WORK/claims.txt"; rm -f "$GN_WORK/editor.json"
export PY=/tmp/claude-0/cvenv/bin/python RUN START=$(date +%s)
printf '{"run": "%s", "start": "%s"}\n' "$RUN" "$(date -Iseconds)" > "$GN_WORK/run.json"
set +e
echo "setup done: $RUN at $(date '+%H:%M') IST, main at $(git rev-parse --short HEAD)"
