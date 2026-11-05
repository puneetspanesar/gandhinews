"""Git merge driver for content/photos.json, content/photos.map.json and content/homepage.json.

Set up once per clone (RUNBOOK.md step 0 does it):
  git config merge.gnjson.name "Gandhi News JSON merge"
  git config merge.gnjson.driver "python3 newsroom/scripts/merge_json.py %O %A %B %P"
.gitattributes routes the three files here.

photos.json (a list of entries with an "id"): union by id; when both sides changed the same id, ours wins.
photos.map.json (story id -> entry): union by key; for a key both sides changed, ours wins.
homepage.json: theirs (the newer homepage from main) wins whole; the run re-applies its own picks afterwards
  with refresh_home.py. The driver prints a note so the run knows.
Exit 0 with the merged result written to %A; exit 1 (leave a conflict) only when a file is not valid JSON.
"""
import json, sys

base_p, ours_p, theirs_p, path = sys.argv[1], sys.argv[2], sys.argv[3], (sys.argv[4] if len(sys.argv) > 4 else '')


def load(p):
    try:
        with open(p) as f: return json.load(f)
    except Exception:
        return None


base, ours, theirs = load(base_p), load(ours_p), load(theirs_p)
if ours is None or theirs is None:
    sys.stderr.write(f'merge_json: {path} is not valid JSON on one side; leaving a conflict\n'); sys.exit(1)

if path.endswith('homepage.json'):
    out = theirs
    sys.stderr.write('merge_json: homepage.json taken from main; re-run refresh_home.py (with --lead/--pin) to re-apply this run\'s picks\n')
elif isinstance(ours, list):
    base_ids = {e.get('id'): e for e in (base or []) if isinstance(e, dict)}
    out, seen = [], {}
    for e in theirs:
        seen[e.get('id')] = len(out); out.append(e)
    for e in ours:
        i = e.get('id')
        if i in seen:
            if e != base_ids.get(i): out[seen[i]] = e  # ours changed it: ours wins
        elif i not in base_ids:
            seen[i] = len(out); out.append(e)        # new on our side
        # in base, not in theirs: theirs deleted it; keep it deleted unless ours changed it
        elif e != base_ids.get(i):
            seen[i] = len(out); out.append(e)
else:
    base = base or {}
    out = dict(theirs)
    for k, v in ours.items():
        if k not in theirs:
            if k not in base or v != base.get(k): out[k] = v
        elif v != base.get(k):
            out[k] = v
    for k in base:
        if k not in ours and k in out and out[k] == base[k]: del out[k]  # ours deleted, theirs untouched
with open(ours_p, 'w') as f:
    json.dump(out, f, ensure_ascii=False, indent=2 if 'homepage' in sys.argv[-1] else 1)
    f.write('\n')
