"""Apply the editor's verdict before publishing. The editor agent writes $GN_WORK/editor.json:
  {"verdict": "PASS" | "FAIL", "fail": [{"id": "<story id>", "why": "<reason>", "kind": "picture" | "facts" | "other"}], "homepage": "ok" | "<what is wrong>"}
Every failed story is moved to newsroom/held/{en,hi}/ with a reason file newsroom/held/<id>.json
({"why", "kind": "picture" | "facts" | "other", "held_at"}), and refresh_home.py is re-run so the homepage
never points at a held story. Exit 0 when everything left is publishable; 1 when the homepage itself failed or a FAIL listed nothing
(fix it and ask a NEW editor); 2 when editor.json is missing, malformed or its nonce is not this review pack's;
3 when a hold could not be made (a script error: fix the id and run again).
Only "picture" holds may ever be republished automatically (once a correct picture exists); "facts" and
"other" holds need the owner or a new editor PASS.
"""
import json, os, sys, glob, shutil, subprocess, datetime as dt
import os as _gn_os; GN_ROOT = _gn_os.environ.get('GN_ROOT') or _gn_os.path.dirname(_gn_os.path.dirname(_gn_os.path.dirname(_gn_os.path.abspath(__file__)))) + '/'
W = os.environ.get('GN_WORK') or '/home/claude/gn-work/'
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
try:
    v = json.load(open(W + 'editor.json'))
    assert v.get('verdict') in ('PASS', 'FAIL'), 'verdict must be PASS or FAIL'
    nonce = open(W + 'review/list.txt').read().split('NONCE ')[1].split()[0]
    assert v.get('nonce') == nonce, f'nonce {v.get("nonce")!r} does not match this review pack ({nonce}): the editor did not read this pack'
except Exception as e:
    print(f'apply_verdict: {W}editor.json missing or malformed ({e}); run the editor check first'); sys.exit(2)
os.chdir(GN_ROOT)
moved = []
for f in v.get('fail') or []:
    sid, why = f.get('id'), f.get('why', '')
    if not sid or sid == 'homepage':
        v['homepage'] = (v.get('homepage') if v.get('homepage') not in ('ok', 'OK', None, '') else '') + ' ' + why; continue
    kind = f.get('kind') if f.get('kind') in ('picture', 'facts', 'other') else 'picture' if any(w in why.lower() for w in ('picture', 'photo', 'image', 'graphic', 'cover')) else 'facts' if any(w in why.lower() for w in ('fact', 'figure', 'number', 'wrong', 'false', 'stale', 'date')) else 'other'
    r = subprocess.run([sys.executable, 'newsroom/scripts/held.py', 'hold', sid, kind, why])
    if r.returncode: print(f'apply_verdict: could not hold {sid}'); sys.exit(3)
    moved.append(f'{sid} ({kind}: {why})')
if moved:
    print('held:'); [print('  ' + m) for m in moved]
    subprocess.run([sys.executable, 'newsroom/scripts/refresh_home.py'], check=False)
for f in v.get('fixed') or []: print(f"fixed by the run, not re-checked by the editor: {f.get('id')}: {f.get('why')} -> {f.get('done')}")
hp = str(v.get('homepage') or '').strip()
if hp.lower().rstrip('.') not in ('ok', ''):
    print(f'homepage failed the editor check: {hp}'); sys.exit(1)
if v['verdict'] == 'FAIL' and not moved and not v.get('fixed'): print('editor said FAIL but listed nothing to hold or fix: ask a NEW editor agent'); sys.exit(1)
print('verdict applied: ' + ('PASS' if not moved else f'{len(moved)} held, the rest publishable'))
