# Gandhi News: the rules and the shared procedures

Every scheduled run (hourly, long-form, stall check) follows this file plus its own runbook. Work alone: nobody is watching, so never stop to ask a question. Decide, write the decision in the run record, carry on. Where anything else (an old brief, editor-notes.md, a memory of "how it was done before") disagrees with this file, this file wins.

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
13. The lead is the biggest story in India right now, under 8 hours old, never a markets story, with a real photo.
14. Top headlines: news from the last 24 hours, at most ONE markets story, at most TWO per section in the top eight, never two stories on the same subject side by side, no photo twice.
15. The site visibly changes every hour: new stories, a refreshed homepage, current markets figures during market hours.
16. No empty space, empty slot, camera placeholder, grey text, pill, gradient or shadow anywhere (check_layout.cjs).

Run discipline
17. Nothing reaches main before the gate (section D). No pushes mid-run.
18. Never get around a site that blocks automated reading. Never paste keys. Never force-push main or rewrite its history. Commits are by Claude <noreply@anthropic.com> and end with the attribution lines from the session's system reminder.
19. The owner hears only about problems a run could not fix (a held story, a broken build it could not repair). A normal run sends nothing.

## B. Setup (first thing in every run)
```
cd /home/claude/gandhinews 2>/dev/null || cd /home/claude
[ -f /home/claude/gandhinews/newsroom/scripts/setup.sh ] || gh repo clone puneetspanesar/gandhinews /home/claude/gandhinews
source /home/claude/gandhinews/newsroom/scripts/setup.sh <run-name>     # hourly-HH, longform-m, longform-e
bash newsroom/scripts/lock.sh take <run-name> <minutes>                  # hourly 50, long-form 80
```
lock.sh exit 3 means another run holds the lock: `bash newsroom/scripts/lock.sh wait <run-name> <minutes>` waits until it is free or stale (a hold past its time is stale and is taken over). Release it at the very end, also after a failure: `bash newsroom/scripts/lock.sh release <run-name>`.
Then the held stories: `python3 newsroom/scripts/held.py expire`, `python3 newsroom/scripts/held.py list`, and `held.py republish <id>` for each picture hold whose picture now exists (then set its `published:` to now only if the news is still current; otherwise leave the time and let it sit below the top).

## C. Pictures (in this order, for every new story)
1. INSTANT, photos we already have: `python3 newsroom/scripts/quick_photo.py <id> "<subject>" --list`, look at the candidates, then `--pick <photo-id>`. Subject = the person as Wikipedia names them, or the place. Seconds.
2. FINDER for every story still without a correct picture, all in ONE call per run: write queries to $GN_WORK/q-<tag>.json (`{"k1": "Rahul Gandhi||8", "k2": "Chennai floods||8"}`), then `python3 newsroom/scripts/photos_gh.py find <tag> $GN_WORK/q-<tag>.json` (about 2 minutes). Look at the thumbnails (make one contact sheet and Read it), pick by eye, then for each pick `python3 newsroom/scripts/one_photo.py <id> $GN_WORK/pcv<tag> <key> <n> "<English alt>" "<Hindi alt>"` (downloads, crops, registers; about 1 minute). Alt text names what is shown; "(file photo)" when it is not from this event.
   Two-person splits and covers: the long procedure in newsroom/PHOTOS-COMPOSITE.md, only when there is time.
3. INFOGRAPHIC, last resort, only under rule 11: `python3 newsroom/scripts/make_infographic.py <id> ...`.
4. No correct picture by the picture deadline: `python3 newsroom/scripts/held.py hold <id> picture "no correct photo of <subject>"`. Never a wrong or generic photo.
In-story ```photo blocks whose photo did not arrive are deleted from both language files; the story still goes.
Wrong picks go into newsroom/scripts/blocklist.txt (file name, lower case) so no later run picks them again.

## D. The gate (every run, in this order, nothing skipped)
```
python3 newsroom/scripts/refresh_home.py [--lead <id>] [--pin <id> ...]
python3 newsroom/scripts/check_fresh.py              # must print OK
npm run -s check:photos                               # must print OK
npm run build > $GN_WORK/build.log 2>&1; echo build=$?   # must be 0: it includes check-links and the build gate
python3 newsroom/scripts/audit.py --changed           # content, photos, home, site, style on what this run changed
node newsroom/scripts/check_layout.cjs                # desktop, phone, Hindi: no empty space, no unloaded pictures
```
Never pipe the build into grep or tail before reading its exit code. Fix every failure at its cause (the story, the picture, homepage.json), then run the whole gate again from the top. A story that cannot be fixed in 5 minutes is held with held.py and the gate is run again.
Then the editor's check: `python3 newsroom/scripts/review_pack.py <ids of this run's stories>`, then ONE fresh agent (general-purpose, it did none of this run's work) with the prompt `Read /home/claude/gandhinews/newsroom/briefs/editor-check.md and follow it exactly.` It writes $GN_WORK/editor.json. A FIX you can make in 5 minutes without new research (drop an in-story photo, swap in a photo already checked, fix a word or a figure the editor quoted) you may make first: then move that entry from `fail` to a `fixed` list in editor.json with what you did (`{"id", "why", "done"}`), so the record shows it. Then `python3 newsroom/scripts/apply_verdict.py`: it holds every failed story (with its reason) and refreshes the homepage. Exit 1 means the homepage itself failed: fix it and ask a NEW editor agent once more. After apply_verdict, run the gate's first four lines again (refresh_home, check_fresh, check:photos, build).

## E. Publish (only after D passes)
```
python3 newsroom/scripts/run_record.py write <run-name> "<one-line summary>"   # newsroom/runs/<date>-<run>.json
git add -A content public/photos newsroom && git commit -q -F $GN_WORK/commit.txt
git pull -q origin main && npm run build > $GN_WORK/build.log 2>&1 && git push -q origin HEAD:main; echo push=$?
bash newsroom/scripts/lock.sh release <run-name>
```
The commit message starts "Hourly HH:00 IST:" or "Long-form morning|evening:", lists the stories, holds and the editor verdict, and ends with the attribution lines. If the pull merged anything, the rebuild after it is the gate on the merged result; a failure there is fixed before pushing.
Then wait for the deploy: `python3 newsroom/scripts/verify_live.py` (poll every minute for up to 10 minutes until the deploy line clears). If it still fails, fix what it says now; whatever is left goes in the run record for the stall check. Then `npm run -s indexnow -- 2`.
