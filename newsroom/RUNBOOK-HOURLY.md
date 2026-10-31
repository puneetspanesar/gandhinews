# Gandhi News hourly update: runbook

One run every hour. Each run publishes AT LEAST 5 new news stories (aim for 6 to 8), refreshes the headlines and the homepage, and keeps the markets band current. Editorials, explainers and other long forms are NOT written here; the twice-daily long-form run (RUNBOOK-LONGFORM.md) does those. Work alone: nobody is watching, so never stop to ask a question. Decide, note the decision in the report, and carry on. The whole run must finish inside 45 minutes; cut volume (never pictures or checks) if time runs short.

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
If that prints a line `busy <ISO time>` less than 55 minutes old, another run is still working: check again every 2 minutes for up to 20 minutes; if it is still busy, stop (no message), the next hour picks up the gap. Otherwise take the lock:
```
lock() { d=$(mktemp -d); git -C "$d" init -q; printf '%s\n' "$1" > "$d/lock.txt"; git -C "$d" add lock.txt; git -C "$d" -c user.name=desk -c user.email=desk@gandhinews.com commit -qm lock; git -C "$d" push -qf "$(git remote get-url origin)" HEAD:refs/heads/run-lock; rm -rf "$d"; }
lock "busy $(TZ=Asia/Kolkata date -Iseconds) hourly"
```
Release it at the very end, also when the run fails part-way: `lock "free"`.

Then do RUNBOOK.md step 0 (npm ci, gn-work copy, Python venv, empty claims.txt). Window: THE LAST 2 HOURS ONLY (`TZ=Asia/Kolkata date`). The 6 am run covers from midnight. This is an hourly desk: it publishes the latest news, never a catch-up. Never go back further because earlier runs were missed or the site looks thin: news older than the window is gone; if it develops, the new development is the story. A story counts as in the window only if the EVENT itself (the announcement, the verdict, the match result, the statement) happened inside it, judged from the source's own time stamp, not from when an article about it was posted or found. A preview of something later today or tomorrow is fine; a recap of yesterday is not. If the window really has fewer than 5 new stories, write fresh developments of running stories (with new facts from inside the window) before ever reaching back; if still short, publish what is real and say so in the report.

## 1. Desks (three in parallel)
Edit the window lines in gn-work/desk-addendum-v2.md and gn-work/run-brief.md as RUNBOOK.md step 1 says (published times inside this window). Add to run-brief.md: "This is an HOURLY run. Write only news briefs and leads, no explainers or editorials. Max 6 WebSearch calls per desk."

Launch THREE desk agents in ONE message (general-purpose, parallel), each prompt starting `Read /home/claude/gn-work/run-brief.md and follow it. DESK = <desk>.`:
1. india: national politics, courts, states, policy, PIB, Parliament. 2 or 3 stories.
2. world-business: world news with India angles, economy, markets, companies, RBI/SEBI. 2 or 3 stories. During market hours (9:15 to 15:30 IST, Monday to Friday, not NSE holidays) one of them is a market story when the market moved.
3. sport-science: cricket first, other sport, science, tech, space, health, climate. 1 or 2 stories.
Only news whose event happened inside the 2-hour window (check the time in the source), or a real new development on an older story (new slug). Desks must put the event time in `verification.notes`, e.g. "event: 31 Oct 21:40 IST, statement on X". Any story whose event is older than the window is deleted before commit. Leads 400 to 650 words when the news deserves it; most hourly stories are briefs (220 to 380 words). Every story bolds its key phrases in the body and carries its in-story visuals (briefs 2, leads 3), as desk-addendum-v2.md says. Wait for all three, then validate and commit the stories exactly as RUNBOOK.md step 1 says. If fewer than 5 stories came back, launch one more agent for the gap before moving on.

## 2. Pictures
RUNBOOK.md step 2, with a fresh tag per run: `h<day><hour>` (e.g. `h0114` for 14:00 on the 1st). Each story now brings 2 or 3 in-story photos as well as its main picture, so expect two or three finder parts. Check the in-story photos by eye exactly like main photos (right person, right place). Small runs usually need one fallback round. A story still without a correct picture after the fallback round is NOT published: move both language files to newsroom/held/ (create it) and note it in the report; the next run tries again.

## 3. Markets and data (content/data/markets.json)
Format: newsroom/markets-format.md. Update every run:
- Market hours: current levels of the indices in the file, change and % change on the previous close, `status: "open"`, `as_of` = now. Also rupee, Brent, gold, silver, 10-year G-sec yield, top Nifty gainers and losers, sector moves.
- After 15:30 IST on a trading day: the closing values, `status: "closed"`; append that day's close to each index `history` (keep the last 30 sessions), FII/DII provisional flows when NSE has published them.
- Outside trading days: leave values, only refresh global items that move (Brent, gold) when there is a newer settle.
- Every number from a source you actually read in this run (exchange, RBI, CCIL, or a major business site). Never estimate. If a value cannot be found, keep the old one and its old date, never invent a new one.
- When an economy release lands (CPI, IIP, GDP, GST, forex reserves, repo), update content/data/economy-dashboard.json and its Hindi twin as RUNBOOK.md step 1 describes.
Max 6 WebSearch calls for this step.

## 4. Homepage (every run)
Update content/homepage.json as RUNBOOK.md step 3 describes, with this run's stories in mind:
- Everything at the top of the page is LATEST news. lead: the biggest story of the last 12 hours (replace it when the current one is older or something bigger broke). Live band (lead.relatedBelow), relatedBeside, briefing and topStories: news published in the last 24 hours, newest first. Drop any preview whose event has now passed (a headline saying something "plans", "will" or "to" happen on a date that is over) and any dataBox item about a date that is over. When the running story continues, keep lead.live.title and put its newest developments in relatedBelow.
- topStories, briefing (8 items, newest news first; their short leads feed the running-stories strip), section and desk lists: put this run's stories in, newest first, and drop the oldest.
- opinion and startHere: newest editorials and explainers first (the long-form run writes them; just pick them up).
- weekAhead: drop past items.
Every id must exist (the example script checks this).

## 5. Build, publish, report
First `python3 newsroom/scripts/check_fresh.py` must print OK (fix homepage.json until it does). Then RUNBOOK.md step 4 (check:photos, clean build with no errors). Commit with the message "Hourly update <HH>:00 IST: N stories", push, then release the lock. When the Cloudflare build for that commit has finished (`gh api repos/puneetspanesar/gandhinews/commits/<sha>/check-runs`), tell other search engines about the new pages: `npm run -s indexnow -- 2`. Send one short SendUserMessage only when something needs the owner: a story held for lack of a picture, a failed build, a doubtful story removed, or fewer than 5 stories. A normal run sends nothing.
