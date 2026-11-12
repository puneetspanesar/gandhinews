#!/usr/bin/env python3
"""Tests for the collage tool (owner, November 12). Run before any change to treat_photo.py ships; the gate runs it
whenever that file differs from the live one.

  python3 newsroom/scripts/test_collage.py          exit 0 all hold | 1 a rule that held is now broken

newsroom/tests/collage/cases.json lists fixed photos and what the cut-out step must say about each:
  clean    one person with shoulders, usable as the subject in front
  cropped  a person whose head touches the top: only as a last resort, never when a clean portrait exists
  reject   a place, a group, a face filling the frame, a half-hidden person: never the subject
A case marked known_failure is a mistake the tool still makes: it is reported, does not fail the run, and the mark
must be removed once the tool gets it right (the run fails if a known failure now passes, so the mark cannot go stale).
To add a case after any wrong collage on the site: copy the photo in, add a line with what it should have said."""
import json, os, sys, warnings
warnings.filterwarnings('ignore')
R = os.path.dirname(os.path.abspath(__file__)) + '/../../'
os.chdir(R); sys.path.insert(0, 'newsroom/scripts')
import treat_photo as T
from PIL import Image
D = 'newsroom/tests/collage/'
bad, known, fixed = [], [], []
cases = json.load(open(D + 'cases.json'))
for c in cases:
    im = Image.open(D + c['file']).convert('RGB')
    r = T._cuts_v(im) or T._cuts(im)
    got = 'reject' if not r else ('cropped' if r[1] else 'clean')
    ok = got in c['want']
    if c.get('known_failure'):
        (fixed if ok else known).append((c, got))
    elif not ok: bad.append((c, got))
for c, got in known: print(f"known   {c['file']}: says {got}, should be {' or '.join(c['want'])} ({c['why']})")
for c, got in fixed: print(f"FIXED   {c['file']}: now right ({got}); remove its known_failure mark in cases.json")
for c, got in bad: print(f"BROKEN  {c['file']} ({c['shows']}): says {got}, must be {' or '.join(c['want'])}: {c['why']}")
print(f'{len(cases) - len(bad) - len(known) - len(fixed)} of {len(cases)} hold, {len(known)} known failures, {len(bad)} broken')
sys.exit(1 if bad or fixed else 0)
