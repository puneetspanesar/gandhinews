"""Apply the editor's verdict before publishing. The editor agent writes $GN_WORK/editor.json:
  {"verdict": "PASS" | "FAIL", "fail": [{"id": "<story id>", "why": "<reason>", "kind": "picture" | "facts" | "other"}], "homepage": "ok" | "<what is wrong>"}
Every failed story is moved to newsroom/held/{en,hi}/ with a reason file newsroom/held/<id>.json
({"why", "kind": "picture" | "facts" | "other", "held_at"}), and refresh_home.py is re-run so the homepage
never points at a held story. Exit 0 when everything left is publishable; 1 when the homepage itself failed
(fix it and ask the editor again); 2 when editor.json is missing or malformed.
Only "picture" holds may ever be republished automatically (once a correct picture exists); "facts" and
"other" holds need the owner or a new editor PASS.
"""
import json, os, sys, glob, shutil, subprocess, datetime as dt
import os as _gn_os; GN_ROOT = _gn_os.environ.get('GN_ROOT') or _gn_os.path.dirname(_gn_os.path.dirname(_gn_os.path.dirname(_gn_os.path.abspath(__file__)))) + '/'
W = os.environ.get('GN_WORK') or '/home/claude/gn-work/'
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
try:
    v = json.load(open(W + 'editor.json'))
    assert v.get('verdict') in ('PASS', 'FAIL')
except Exception as e:
    print(f'apply_verdict: {W}editor.json missing or malformed ({e}); run the editor check first'); sys.exit(2)
os.chdir(GN_ROOT)
moved = []
for f in v.get('fail') or []:
    sid, why = f.get('id'), f.get('why', '')
    kind = f.get('kind') if f.get('kind') in ('picture', 'facts', 'other') else 'picture' if any(w in why.lower() for w in ('picture', 'photo', 'image', 'graphic', 'cover')) else 'facts' if any(w in why.lower() for w in ('fact', 'figure', 'number', 'wrong', 'false', 'stale', 'date')) else 'other'
    for lang in ('en', 'hi'):
        for p in glob.glob(f'content/{lang}/*/{sid}.md'):
            os.makedirs(f'newsroom/held/{lang}', exist_ok=True)
            subprocess.run(['git', 'mv', '-f', p, f'newsroom/held/{lang}/{sid}.md'], check=False) if subprocess.run(['git', 'ls-files', '--error-unmatch', p], capture_output=True).returncode == 0 else shutil.move(p, f'newsroom/held/{lang}/{sid}.md')
    json.dump({'why': why, 'kind': kind, 'held_at': dt.datetime.now(IST).isoformat(timespec='minutes')}, open(f'newsroom/held/{sid}.json', 'w'), ensure_ascii=False, indent=1)
    moved.append(f'{sid} ({kind}: {why})')
if moved:
    print('held:'); [print('  ' + m) for m in moved]
    subprocess.run([sys.executable, 'newsroom/scripts/refresh_home.py', '--keep'], check=False)
hp = v.get('homepage', 'ok')
if hp not in ('ok', 'OK', '', None):
    print(f'homepage failed the editor check: {hp}'); sys.exit(1)
print('verdict applied: ' + ('PASS' if not moved else f'{len(moved)} held, the rest publishable'))
