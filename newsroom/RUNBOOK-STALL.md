# Stall check (minute 52 of every hour, 7 am to 11 pm IST)

The counter check on the hourly and long-form runs. It never trusts a run's own report: it checks the live site against the rules and fixes what is wrong. Read newsroom/RUNBOOK.md first; its rules (A), pictures (C), gate (D) and publish (E) apply. The owner hears from this run only about what it could not fix.

## 1. Check (about 5 minutes)
```
source /home/claude/gandhinews/newsroom/scripts/setup.sh stall-HH
python3 newsroom/scripts/verify_live.py          # deploy, missed runs, homepage rules, lead shown, empty slots, holds
python3 newsroom/scripts/run_record.py last      # what the last run says it did: editor verdict, holds, breaches
bash newsroom/scripts/gate.sh                    # the same gate the runs use, on main as it is now
```
All three clean: finish silently.

## 2. Decide
- No "Hourly HH:00" commit on main yet this hour (`git log --since="60 minutes ago" --format=%s origin/main`): the hourly run is late or failed. Act.
- The last run record shows an editor FAIL with nothing held, no editor.json, breaches, or holds that verify_live says can be republished: act.
- verify_live or gate.sh fails: act.

## 3. Fix (inside 30 minutes), at the cause
- Deploy stuck (the live site is behind main): the build gate fails on Cloudflare. gate.sh shows why; fix it (a picture through section C, a Hindi twin, page junk, a date or dash), or hold the story with held.py.
- Stale figures tied to a clock time: look up the latest figure (WebSearch, WebFetch; never estimate) and update the story in both languages: title, standfirst, first key point, first paragraph, overlay, its infographic block (then make_infographic.py), `updated:` and the source. If there is no newer figure anywhere, take the story off the top.
- Lead or headlines breaking the rules: `refresh_home.py --lead <id>` with the biggest story of the last 8 hours that has a real photo, never a markets story.
- A missed run: refresh the homepage and the markets figures (content/data/markets.json, newsroom/markets-format.md) from sources read now.
- Picture holds whose new picture exists: `held.py republish <id>`.
Then gate.sh until it passes (add the editor check of RUNBOOK.md D only if you wrote or rewrote a story), commit.txt starting "Stall fix HH:MM IST:", and `bash newsroom/scripts/publish.sh stall-HH "<summary>"`.

## 4. Report
Only what is still wrong after the fix: ONE short SendUserMessage, "Gandhi News check, <time> IST:" and one plain line per problem. Nothing when everything was fixed.
