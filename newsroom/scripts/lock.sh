#!/usr/bin/env bash
# The publish lock: only one task at a time may merge into main and push (the short "promote" step).
# Everything else (desks, pictures, building) runs without the lock. Append-only history on the
# run-lock branch; taking it is compare-and-swap (a plain, non-force push that fails if anyone else
# moved the branch first), so two tasks can never both hold it.
#   newsroom/scripts/lock.sh take <owner> [ttl_minutes=15]   exit 0 = taken, 3 = busy (prints holder)
#   newsroom/scripts/lock.sh wait <owner> [max_minutes=12] [ttl=15]  take, retrying every 20 s
#   newsroom/scripts/lock.sh release <owner>                 only the holder can release
#   newsroom/scripts/lock.sh status
# <owner> is e.g. hourly-1405, longform-e05, stallfix-1452. A lock older than its ttl is free.
set -u
cd "$(git rev-parse --show-toplevel)"
REMOTE=$(git remote get-url origin)
REF=${LOCKREF:-run-lock}
read_lock() {
  git fetch -q origin +refs/heads/$REF:refs/remotes/origin/$REF 2>/dev/null || { SHA=""; LINE="free"; return; }
  SHA=$(git rev-parse refs/remotes/origin/$REF)
  LINE=$(git show "$SHA:lock.txt" 2>/dev/null | head -1)
}
now() { date +%s; }
is_free() {  # free, expired, or held by $1
  case "$LINE" in busy*) ;; *) return 0;; esac
  set -- $LINE  # busy <epoch> <owner> <ttl>
  local t=$2 who=$3 ttl=${4:-15}
  case "$t" in *[!0-9]*) t=$(date -d "$t" +%s 2>/dev/null || echo 0);; esac  # old-style ISO time
  [ "$who" = "$OWNER" ] && return 0
  [ $(( $(now) - t )) -gt $(( ttl * 60 )) ] && return 0
  return 1
}
write_lock() {  # $1 = new line; commit on top of $SHA and push without force
  local d tree c
  d=$(mktemp -d); printf '%s\n' "$1" > "$d/lock.txt"
  tree=$(git mktree <<< "100644 blob $(git hash-object -w "$d/lock.txt")	lock.txt"); rm -rf "$d"
  if [ -n "$SHA" ]; then c=$(git -c user.name=Claude -c user.email=noreply@anthropic.com commit-tree "$tree" -p "$SHA" -m "$1")
  else c=$(git -c user.name=Claude -c user.email=noreply@anthropic.com commit-tree "$tree" -m "$1"); fi
  git push -q "$REMOTE" "$c:refs/heads/$REF" 2>/dev/null
}
cmd=${1:-status}; OWNER=${2:-}
case "$cmd" in
  status) read_lock; echo "$LINE";;
  take)
    TTL=${3:-15}
    for i in 1 2 3 4 5; do
      read_lock
      if ! is_free; then echo "busy: $LINE"; exit 3; fi
      write_lock "busy $(now) $OWNER $TTL $(TZ=Asia/Kolkata date +%H:%M)" && { echo "taken by $OWNER"; exit 0; }
      sleep 2  # someone moved the branch between our read and push: re-read and retry
    done
    echo "could not take the lock (push kept failing)"; exit 4;;
  wait)
    MAX=${3:-12}; TTL=${4:-15}; end=$(( $(now) + MAX * 60 ))
    while :; do "$0" take "$OWNER" "$TTL" && exit 0; [ $? -eq 4 ] && exit 4; [ "$(now)" -ge "$end" ] && { echo "gave up after $MAX minutes"; exit 3; }; sleep 20; done;;
  release)
    for i in 1 2 3 4 5; do
      read_lock
      case "$LINE" in busy*) set -- $LINE; [ "$3" != "$OWNER" ] && { echo "not released: held by $3"; exit 0; };; *) echo "already free"; exit 0;; esac
      write_lock "free $(now) $OWNER" && { echo "released"; exit 0; }
      sleep 2
    done; exit 4;;
  *) echo "usage: lock.sh take|wait|release|status <owner>"; exit 2;;
esac
