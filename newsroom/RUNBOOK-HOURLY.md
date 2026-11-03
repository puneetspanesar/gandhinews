# Gandhi News hourly update: runbook

One run every hour. Each run publishes 3 to 6 new news stories, refreshes the homepage, and keeps the markets band current. Editorials, explainers and other long forms are NOT written here; the twice-daily long-form run (RUNBOOK-LONGFORM.md) does those. Work alone: nobody is watching, so never stop to ask a question. Decide, note the decision in the report, and carry on.

## THE FIRST RULE: THE SITE MUST CHANGE EVERY HOUR
On November 3, 2026 the site sat still from 3 pm to 7 pm because runs wrote stories but held them all while covers, extra photos and editor rounds ran out of time, and runs then blocked each other. The owner noticed. Never again:
- Note the start time. Hard checkpoints (minutes from the start): desks done by 15, main pictures done by 30, PUSH by 40, whatever is ready. Anything not ready at 40 is held, never the whole run.
- A story goes live once its text is checked and its MAIN picture is checked by eye. Covers and in-story photos are extras: add them only if time allows, and drop them (never hold a story) when they are not ready or not right.
- The editor check judges each story on its own. A failing story is held or fixed; the others go live. One fix round only.
- Every run ends with a push that changes the homepage (step 4 refresh_home.py), even when no new story was written.
- Held stories: at the start of every run, look in newsroom/held/. Republish any held story under 12 hours old that now has a correct main picture (step 2); delete held stories older than 12 hours (both languages): that news is gone.

Everything in RUNBOOK.md "Standing editorial rules" applies here unchanged (byline, own voice, bold key facts, no em dashes, Hindi twin, unique photos, EVERY story with a correct picture, fact-check/trackers/data/Parliament/standards at the bottom of the homepage).

## 0. Lock, set up, window
```
[ -d /home/claude/gandhinews/.git ] || gh repo clone puneetspanesar/gandhinews /home/claude/gandhinews
cd /home/claude/gandhinews && git pull -q
```
Lock (kept on its own branch so it never triggers a site build):
```
git fetch -q origin run-lock 2>/dev/null && git show origin/run-lock:lock.txt 2>/dev/null
```
If that prints a line `busy <ISO time> hourly` less than 50 minutes old, another hourly run is still working: check every 2 minutes for up to 10 minutes; if it is still busy, take the lock anyway (that run is overdue) and go on. A `longform` lock does NOT stop an hourly run: go on and take the lock (the long-form run re-takes it when it pushes; both runs merge on push conflicts as RUNBOOK.md says). An hourly run never skips its hour because of the lock. Take the lock:
```
lock() { d=$(mktemp -d); git -C "$d" init -q; printf '%s\n' "$1" > "$d/lock.txt"; git -C "$d" add lock.txt; git -C "$d" -c user.name=desk -c user.email=desk@gandhinews.com commit -qm lock; git -C "$d" push -qf "$(git remote get-url origin)" HEAD:refs/heads/run-lock; rm -rf "$d"; }
lock "busy $(TZ=Asia/Kolkata date -Iseconds) hourly"
```
Release it at the very end, also when the run fails part-way: `lock "free"`.

Then do RUNBOOK.md step 0 (npm ci, gn-work copy, Python venv, empty claims.txt). Window: THE LAST 2 HOURS ONLY (`TZ=Asia/Kolkata date`). The 6 am run covers from midnight. This is an hourly desk: it publishes the latest news, never a catch-up. Never go back further because earlier runs were missed or the site looks thin: news older than the window is gone; if it develops, the new development is the story. A story counts as in the window only if the EVENT itself (the announcement, the verdict, the match result, the statement) happened inside it, judged from the source's own time stamp, not from when an article about it was posted or found. A preview of something later today or tomorrow is fine; a recap of yesterday is not. If the window really has fewer than 5 new stories, write fresh developments of running stories (with new facts from inside the window) before ever reaching back; if still short, publish what is real and say so in the report.

## 0b. Front-page check (every run, before the desks: this decides what we cover)
First read newsroom/editor-notes.md (the owner's current priorities and known gaps) and treat its items as BIG STORIES; delete each item from that file once published.
We are a general news site and must cover what India is talking about, not what is easiest to source. Most big Indian news homepages block automated reading (never get around that), so spend at most 5 minutes here: try newsonair.gov.in, republicworld.com, timesofindia.indiatimes.com and reuters.com, and run 2 WebSearch calls (mode extended) for India's top news of the last few hours. A story leading two or more of these is a BIG STORY.
- Every BIG STORY we have not covered gets written this run, first, before anything else. The 2-hour window does not apply to a BIG STORY that broke in the last 24 hours and that we have missed; write it with the latest facts.
- Every BIG STORY we already have but whose latest development is missing gets a new development story.
- Put the list (BIG STORIES, ours or missing) at the top of gn-work/run-brief.md so the desks write them first.
- The single biggest story across those front pages is our lead (step 4). Our lead must never be a story the other front pages are not leading with.
Reporting from other outlets is only how we find the news: our stories are still sourced and written in our own voice.

## 1. Desks (three in parallel)
Edit the window lines in gn-work/desk-addendum-v2.md and gn-work/run-brief.md as RUNBOOK.md step 1 says (published times inside this window). Add to run-brief.md: "This is an HOURLY run. Write only news briefs and leads, no explainers or editorials. Max 6 WebSearch calls per desk."

Launch THREE desk agents in ONE message (general-purpose, parallel), each prompt starting `Read /home/claude/gn-work/run-brief.md and follow it. DESK = <desk>.`:
1. india: national politics, courts, states, policy, PIB, Parliament. 2 or 3 stories.
2. world-business: world news with India angles, economy, companies, RBI/SEBI. 2 or 3 stories. At most ONE market story per run (and only when the market really moved: Sensex or Nifty over 0.5%, or a big single stock), at most one Wall Street or global markets story per day (the morning one), and monthly sales figures as ONE roundup story per day, never a story per company.
3. sport-science: cricket first, other sport, science, tech, space, health, climate. 1 or 2 stories.
Desks write the BIG STORIES from step 0b first. Then only news whose event happened inside the 2-hour window (check the time in the source), or a real new development on an older story (new slug). Desks must put the event time in `verification.notes`, e.g. "event: 31 Oct 21:40 IST, statement on X". Any story whose event is older than the window is deleted before commit. Leads 400 to 650 words when the news deserves it; most hourly stories are briefs (220 to 380 words). Every story bolds its key phrases in the body. In-story visuals in hourly runs: at most 1 per brief and 2 per lead, only where a photo really adds something (a second person in the story, the place); no cover block except for the lead story. Wait for all three, then validate and commit the stories exactly as RUNBOOK.md step 1 says. If fewer than 5 stories came back, launch one more agent for the gap before moving on.

## 2. Pictures
RUNBOOK.md step 2, with a fresh tag per run: `h<day><hour>` (e.g. `h0114` for 14:00 on the 1st). MAIN PICTURES FIRST: the first finder part carries only the main pictures, so they arrive fast; in-story photos go in a second part only if it is not yet minute 20. Check every picture by eye (right person, right place, event stories show the event). One fallback round for main pictures, at most. A story still without a correct, current main picture at minute 30 gets an INFOGRAPHIC cover instead: `python3 newsroom/scripts/make_infographic.py <id> ...` (it reads the story's `infographic:` block and registers the cover in content/photos.map.json; look at each result). Never use a wrong or generic photo to avoid this, and never hold a story for a picture any more. Only a story with no `infographic:` block and no picture is held. In-story photo blocks whose photo did not arrive or is wrong are deleted from the text, never a reason to wait. Covers (make_cover.py) only for the lead story and only if done by minute 35; a story without a cover simply shows its main picture.

## 3. Markets and data (content/data/markets.json)
Format: newsroom/markets-format.md. Update every run:
- Market hours: current levels of the indices in the file, change and % change on the previous close, `status: "open"`, `as_of` = now. Also rupee, Brent, gold, silver, 10-year G-sec yield, top Nifty gainers and losers, sector moves.
- After 15:30 IST on a trading day: the closing values, `status: "closed"`; append that day's close to each index `history` (keep the last 30 sessions), FII/DII provisional flows when NSE has published them.
- Outside trading days: leave values, only refresh global items that move (Brent, gold) when there is a newer settle.
- Every number from a source you actually read in this run (exchange, RBI, CCIL, or a major business site). Never estimate. If a value cannot be found, keep the old one and its old date, never invent a new one.
- When an economy release lands (CPI, IIP, GDP, GST, forex reserves, repo), update content/data/economy-dashboard.json and its Hindi twin as RUNBOOK.md step 1 describes.
Max 6 WebSearch calls for this step.

## 4. Homepage (every run)
Run `python3 newsroom/scripts/refresh_home.py` (add `--lead <id>` when a bigger or newer story should lead, `--pin <id> ...` for BIG STORIES that must sit at the top). It fills the headlines, live band, section lists, explainers and opinion with the newest pictured stories under the balance rules below. Then read what it printed and fix by hand anything the rules below still need (news judgement is yours, the script only does the mechanics):
- News judgement first. The lead is the biggest story in India right now (step 0b), and changes when the front pages change. No story stays the lead for more than 8 hours unless it is still leading the other front pages.
- Balance: in the headlines (lead.relatedBeside, topStories, briefing) at most ONE markets or business story (indices, Wall Street, oil, results, sales figures), at most TWO from any one section, and never two stories on the same subject. A running story (a cyclone, a war) gets the lead or the live band, plus at most one more slot.
- Mix: aim for national politics, a state, world, business, sport and courts or policy in the top eight.
- Everything at the top of the page is LATEST news. lead: the biggest story of the last 12 hours (replace it when the current one is older or something bigger broke). Live band (lead.relatedBelow), relatedBeside, briefing and topStories: news published in the last 24 hours, newest first. Drop any preview whose event has now passed (a headline saying something "plans", "will" or "to" happen on a date that is over) and any dataBox item about a date that is over. When the running story continues, keep lead.live.title and put its newest developments in relatedBelow.
- topStories, briefing (8 items, newest news first; their short leads feed the running-stories strip), section and desk lists: put this run's stories in, newest first, and drop the oldest.
- opinion and startHere: newest editorials and explainers first (the long-form run writes them; just pick them up).
- weekAhead: drop past items.
Every id must exist (the example script checks this).

## 4b. Editor's check (never skip; nothing is published until it passes)
After the clean build, and BEFORE the final commit and push:
1. Save the front-page list from step 0b (other sites' top stories, one per line) to /home/claude/gn-work/frontpages.txt.
2. `python3 newsroom/scripts/review_pack.py <ids of this run's stories>` (it screenshots the built homepage and makes one sheet per story).
3. Launch ONE separate agent (Agent tool, general-purpose, a fresh agent that did none of this run's work) with the prompt: `Read /home/claude/gandhinews/newsroom/briefs/editor-check.md and follow it exactly.` Wait for its reply.
4. If it says FAIL, look at each FIX line. Quick fixes (drop an in-story photo, drop a cover, change the lead or headline mix with refresh_home.py, a wording fix) you do at once. A story whose MAIN picture is wrong and cannot be replaced within 5 minutes is held (both files to newsroom/held/). One fix round, then rebuild and push without asking the editor again, unless the homepage itself failed (then one more editor check of the homepage only).
5. The FAIL of one story never holds the others. Never publish the specific thing that failed; publish everything else.
6. Note the editor's final verdict in the commit message ("editor: PASS" or "editor: PASS after fixes: ...").

## 5. Build, publish, report
First `python3 newsroom/scripts/check_fresh.py` must print OK (fix homepage.json until it does). Then RUNBOOK.md step 4 (check:photos, clean build with no errors). Then step 4b, the editor's check, until it passes. Commit with the message "Hourly update <HH>:00 IST: N stories", push, then release the lock. When the Cloudflare build for that commit has finished (`gh api repos/puneetspanesar/gandhinews/commits/<sha>/check-runs`), tell other search engines about the new pages: `npm run -s indexnow -- 2`. Send one short SendUserMessage only when something needs the owner: a story held for lack of a picture, a failed build, a doubtful story removed, or fewer than 5 stories. A normal run sends nothing.
