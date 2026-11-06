# Gandhi News: the rules and the shared procedures

Every scheduled run (hourly, long-form, stall check) follows this file plus its own runbook (RUNBOOK-HOURLY.md, RUNBOOK-LONGFORM.md, RUNBOOK-STALL.md). Work alone: nobody is watching, so never stop to ask a question. Decide, write the decision in the run record, carry on. Where anything else (an old brief, editor-notes.md, a memory of "how it was done before") disagrees with this file, this file wins.

The site is Astro in the private repo puneetspanesar/gandhinews. Cloudflare deploys every push to main, but only if `npm run build` passes: the build ends with scripts/check-links.mjs and scripts/gate.mjs, so a build that breaks a hard rule is never deployed and the last good site stays live.

## A. The owner's rules (never break)
Writing
1. Byline "From the editorial desk". Our own voice. Never name or credit a media outlet to readers; sources live in the front matter `sources:` only.
2. No em dashes anywhere, English or Hindi (the gate fails new stories that have one). En dashes only in number ranges written as "to".
3. Dates: English "November 5, 2026" (month day, year); Hindi "5 नवंबर 2026". Times "4:30 pm IST".
4. Every story has its Hindi twin at content/hi/<same folder>/<same id>.md, following newsroom/briefs/hindi-glossary.md.
5. Bold: every key point carries one **bold** phrase; most body paragraphs bold the one phrase that carries the news (never a whole sentence).
6. A figure tied to a clock time ("30.5% by 1 pm") is stale 2 hours after that time: update the story (title, standfirst, first key point, first paragraph, `updated:`) or move it off the top. Never just reword the time away.

Pictures
7. Every story goes live with a correct main picture, or does not go live (the gate enforces "a picture", the editor and you enforce "correct").
8. The picture shows who the story is ABOUT: the person who spoke or acted first, the person they answered second. A well-known person always gets a PHOTO, never an infographic.
9. Event stories (rain, flood, cyclone, smog, fire, crash, collapse, strike, protest, polling) show the event: a file photo of the same kind of event in the same region is right, labelled "(file photo)". Never a landmark, temple, office building or calm street.
10. No source photo is used again within 7 days (`npm run -s check:photos`), and never twice at the top of the homepage.
11. Infographics only for stories with no person or place to show (index levels, results tables, a policy with numbers), or when the finder truly found nothing. Numbers on a graphic must match the story; re-render it whenever the story's figures change.
12. Credits come from the photo's page, cleaned (gnrules.clean_credit). No "{{", "&amp;", licence boilerplate or uploader phrases.

Homepage (refresh_home.py does the mechanics, check_fresh.py is the counter check)
13. EVERY HEADLINE CHANGES EVERY HOUR: the lead, the live band, the stories beside the lead, the top stories and the briefing are all different stories from the previous hour's homepage. Only nation- or world-changing news may stay, and only as an update: either a new development story (its own id), or the same story with new facts and a new `updated:` time, passed as `refresh_home.py --critical <id>`. refresh_home.py rotates the headlines itself; check_fresh.py checks it against main's homepage of the previous hour in git.
13a. The lead is the biggest story in India right now, under 8 hours old, never a markets story, with a real photo.
14. Top headlines: news from the last 24 hours, at most ONE markets story, at most TWO per section in the top eight, never two stories on the same subject side by side, no photo twice.
15. The site visibly changes every hour: new stories, a refreshed homepage, current markets figures during market hours.
16. No empty space, empty slot, camera placeholder, grey text, pill, gradient or shadow anywhere (check_layout.cjs).

Run discipline
17. Nothing reaches main before the gate (section D). No pushes mid-run.
18. Never get around a site that blocks automated reading. Never paste keys. Never force-push main or rewrite its history. Commits are by Claude <noreply@anthropic.com> and end with the attribution lines from the session's system reminder.
19. The owner hears only about problems a run could not fix (a held story, a broken build it could not repair). A normal run sends nothing.

## B. Setup (first thing in every run)
Every shell call starts fresh (variables do not carry over), so commands below use full paths: the work folder is /home/claude/gn-work/ and the Python with OpenCV is /tmp/claude-0/cvenv/bin/python.
```
[ -f /home/claude/gandhinews/newsroom/scripts/setup.sh ] || gh repo clone puneetspanesar/gandhinews /home/claude/gandhinews
source /home/claude/gandhinews/newsroom/scripts/setup.sh <run-name>     # hourly-HH, longform-m, longform-e, stall-HH
```
Note the start time setup.sh prints. There is no lock to take now: the lock covers only the pull, build and push inside publish.sh (section E), so runs never block each other's work.
Then the held stories: `python3 newsroom/scripts/held.py expire`, `python3 newsroom/scripts/held.py list`, and `held.py republish <id>` for each picture hold that list marks "a new picture exists" (a hold is fixed only by a different picture from the one it was held with). Set a republished story's `published:` to now only if the news is still current.

## C. Pictures (in this order, for every new story)
0. THE PEOPLE LIBRARY, for any story about a person in it (newsroom/library/people.json, about 400 people in the news, every portrait checked): `python3 newsroom/scripts/one_photo.py <id> --person "<name>"` picks the first portrait not used in 7 days, downloads and registers it (about a minute). A person missing from the library goes in newsroom/library/people.tsv so the weekly library run adds them.
1. INSTANT, photos we already have: `python3 newsroom/scripts/quick_photo.py <id> "<subject>" --list`, look at the candidates, then `--pick <photo-id>`. Subject = the person as Wikipedia names them, or the place. Seconds.
2. FINDER for every story still without a correct picture, all in ONE call per run: write the queries to /home/claude/gn-work/q-<tag>.json (`{"k1": "Rahul Gandhi||8", "k2": "Chennai floods||8"}`), then `python3 newsroom/scripts/photos_gh.py find <tag> /home/claude/gn-work/q-<tag>.json` (usually 2 minutes; give up at 6 and fall back to step 3 or a hold). Make one contact sheet of /home/claude/gn-work/pcv<tag>/photo-candidates/thumbs and Read it, pick by eye, then per pick `python3 newsroom/scripts/one_photo.py <id> /home/claude/gn-work/pcv<tag> <key> <n> "<English alt>" "<Hindi alt>"` (downloads, crops, registers; usually 1 minute; run them one after another, never in parallel). Alt text names what is shown, with "(file photo)" when it is not from this event.
   Two-person splits and covers: newsroom/PHOTOS-COMPOSITE.md, only when there is time.
3. INFOGRAPHIC, last resort, only under rule 11: `python3 newsroom/scripts/make_infographic.py <id> ...`.
4. No correct picture by the picture deadline: `python3 newsroom/scripts/held.py hold <id> picture "no correct photo of <subject>"`. Never a wrong or generic photo.
In-story ```photo blocks whose photo did not arrive are deleted from both language files; the story still goes.
Wrong picks go into newsroom/scripts/blocklist.txt (file name, lower case); pick.py, quick_photo.py and one_photo.py never use them again.

## D. The gate (every run, nothing skipped)
```
python3 newsroom/scripts/refresh_home.py [--lead <id>] [--pin <id> ...]   # its arguments are saved and re-applied by publish.sh
bash newsroom/scripts/gate.sh
```
gate.sh runs, in order and reading every exit code: fix_dates on this run's English files, check_fresh, check:photos, the build, check-links, the build gate (gate.mjs), audit.py --changed and check_layout. It ends with one line: `GATE: PASS`, `GATE: PASS WITH BREACHES` (only check_fresh's exit 2: an infographic lead when no fresh story of the running story has a photo, or no new story in 3 hours; publish, they go in the run record, the next run clears them) or `GATE: FAIL` with each failing check's output. Fix every failure at its cause (the story, the picture, homepage.json) and run gate.sh again. A story that cannot be fixed in 5 minutes is held with held.py, then refresh_home and gate.sh again.
Then the editor's check: `python3 newsroom/scripts/review_pack.py <ids of this run's stories>` (it writes /home/claude/gn-work/review/ with a NONCE line in list.txt), then ONE fresh agent (general-purpose, it did none of this run's work) with the prompt `Read /home/claude/gandhinews/newsroom/briefs/editor-check.md and follow it exactly.` It writes /home/claude/gn-work/editor.json with that nonce. A FIX you can make in 5 minutes without new research (drop an in-story photo, swap in a photo already checked, fix a word or a figure the editor quoted) you may make first; then move that entry from `fail` to a `fixed` list in editor.json with what you did (`{"id", "why", "done"}`). Then `python3 newsroom/scripts/apply_verdict.py`: it holds every failed story with its reason and refreshes the homepage. Exit 1: the homepage failed, or a FAIL listed nothing; fix it and ask a NEW editor agent once. Exit 2: editor.json missing or not from this review pack. Exit 3: a hold failed (wrong id); fix and rerun. If apply_verdict held or fixed anything, run gate.sh once more.

## E. Publish (only after D passes)
Write /home/claude/gn-work/commit.txt: first line "Hourly HH:00 IST: ..." or "Long-form morning|evening: ..." or "Stall fix HH:MM IST: ...", then the stories, holds, breaches and the editor verdict, then the attribution lines from the session's system reminder. Then:
```
bash newsroom/scripts/publish.sh <run-name> "<one-line summary>"
```
publish.sh writes the run record (newsroom/runs/), commits, takes the lock only for the pull, build and push, re-applies this run's homepage picks if the pull merged another run's work (and stops if check_fresh then fails), runs the full build with its build gate, pushes, releases the lock, and waits until the live site runs the pushed commit (verify_live.py --expect). Exit 0: live. Exit 1: not pushed; fix what it printed and run it again. Exit 4: pushed but not live after 12 minutes; read verify_live's output, fix the cause (usually the build gate on Cloudflare) and publish again. Then `npm run -s indexnow -- 2`.
