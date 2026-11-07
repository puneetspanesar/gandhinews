# Writing run (every 2 hours: 6, 8, 10 am, noon, 2, 4, 6, 8, 10 pm and 12:03 am IST; the run name stays hourly-HH)

In the hours between, the GitHub job .github/workflows/home-rotate.yml rotates the homepage at :50 without AI (refresh_home.py and check_fresh.py), so every headline still changes every hour. Markets figures are updated by these runs, so every 2 hours.

Read newsroom/RUNBOOK.md first: its rules (A), setup (B), pictures (C), gate (D) and publish (E) are part of this runbook. This file only adds what is particular to the hourly run.

Each run publishes 8 new news stories (at least 5; the homepage changes every headline every hour, so it needs a steady supply), refreshes the homepage and keeps the markets band current. No explainers or editorials: the long-form runs write those.

## Time budget (minutes from the start time setup.sh printed)
- 0 to 6: setup (a fresh container installs for 2 to 3 minutes), held stories, front-page check.
- 6 to 22: desks write the stories and place their main pictures; then `audit.py --new` on them.
- 22 to 28: pictures the desks could not place (C), and the markets work.
- 28: picture deadline. Every story still without a correct main picture gets its infographic with `--nophoto` (RUNBOOK.md rule 11a) and publishes; it stays out of the top five.
- 28 to 40: refresh_home and gate.sh (about 3 minutes), review_pack and the editor agent, apply_verdict, gate.sh again only if something was held or fixed.
- by 45: publish.sh. If the gate still fails at 42, hold the failing stories and publish the rest. The run ALWAYS publishes, at the least a refreshed homepage and current markets figures, because the site must change every hour.

## 1. Front-page check (5 minutes at most)
Read newsroom/editor-notes.md (the owner's current priorities); its items are BIG STORIES. Then two WebSearch calls (mode extended) for India's top news of the last few hours, and WebFetch of newsonair.gov.in and one or two front pages that allow it. A story leading two or more of them is a BIG STORY. Write the BIG STORIES, ours or missing, to /home/claude/gn-work/frontpages.txt, one per line. Missing BIG STORIES are written first this run, even if they broke up to 24 hours ago; BIG STORIES we have but whose latest development is missing get a development story. Delete an editor-notes item once it is published.

## 2. Desks (four agents in ONE message, in parallel; each finds its own pictures)
Write /home/claude/gn-work/window.txt with: the date and time now (`date`); the window (the last 2 hours; the 6 am run covers from midnight); the BIG STORIES; and these limits, which override every brief: "HOURLY run. News only: briefs 220 to 380 words, leads 400 to 650. Your desk writes the number of stories in its DESK line, and at least one of them must be able to lead: a fresh national, state or world story of real weight with a real photo, never markets, sport or science (those never lead unless the front-page check pins a BIG STORY). In-story photo blocks: at most 1 per brief, 2 per lead, each a different person or place; no cover blocks. At most 6 WebSearch calls." Spawn every desk with `model: "sonnet"` (the owner's usage decision, November 6; the editor agent stays on the default model). Each desk prompt starts `Read /home/claude/gn-work/run-brief.md and follow it. DESK = <desk>.`:
1. national: politics, Parliament, the Union government, courts. 2 stories.
2. states: state politics, governments, disasters, crime and civic news from the states. 2 stories.
3. world-business: 2 stories, ONE of them world news (the homepage World desk needs 4 stories from the last 48 hours; a run without a world story leaves it off the page), the other economy, companies, RBI or SEBI. At most one markets story per run, and only when the market really moved (Sensex or Nifty over 0.5%, or a big single stock); monthly sales figures as one roundup a day.
4. sport-science: 2 stories, ONE of them science, tech, space, health or climate (same reason: the Science desk), the other sport, cricket first. A foreign tennis or football result is not news for this site unless an Indian is in it or it is a final.
5. ONLY in the 12:03 pm and 10:03 pm runs, a fifth desk, opinion-and-fact-check (also Sonnet): 1 editorial and 1 fact check on the biggest issues since the last long-form run that have none yet, following RUNBOOK-LONGFORM.md desks 2 and 3 (shapes, word counts, primary sources only). Its window.txt line: "LONG-FORM pieces inside a writing run: editorial 500 to 800 words with 1 or 2 visuals; fact check against primary sources only." Between these and the three long-form runs the opinion and fact-check sections change several times a day.
That is 8 stories a run, at least 5; the homepage needs them, because every headline changes every hour and the top five never repeat within 6 hours.
PICTURES ARE THE DESK'S JOB, done before it hands back (run-brief.md "Main picture"): the people library first (`one_photo.py <id> --person "<name>"`, seconds), then quick_photo.py, then ONE finder call for whatever is left, then the infographic with `--nophoto` (never a hold for want of a photo). The run then only checks the pictures and does the finder for anything a desk could not place.
An event older than the window is not news; only a real new development of it is (new id). Desks put the event time in `verification.notes`.
When they finish: `python3 newsroom/scripts/audit.py --new --skip photos,home,site,style` checks only the files this run wrote; it must pass (fix the file, or delete that story in both languages), then `git add content public/photos && git commit -q -m "desk HH"` locally. Never push here.

## 3. Pictures
For stories the desks could not picture: RUNBOOK.md section C, tag `h<day><HH>`. Upgrades in the same finder call: `python3 newsroom/scripts/audit.py --hours 24 --skip content,home,site,style` lists stories of the last 24 hours that show an infographic although they are about a person or place. Add those people and places to this run's queries and replace each graphic with the photo (one_photo.py replaces the map entry).

## 4. Markets and data (content/data/markets.json, format in newsroom/markets-format.md)
Market hours (9:15 am to 3:30 pm, Monday to Friday): current index levels, change and % change on the previous close, `status: "open"`, `as_of` now; also rupee, Brent, gold, silver, the 10-year yield, top Nifty gainers and losers, sector moves. After 3:30 pm: closing values, `status: "closed"`, the close appended to each index `history` (last 30 sessions), FII and DII flows once NSE has published them. Every number from a source read in this run; a value you could not find keeps its old value and date. Economy releases (CPI, IIP, GDP, GST, forex reserves, repo) also update content/data/economy-dashboard.json and its Hindi twin. At most 6 WebSearch calls.

## 5. Homepage, gate, editor, publish
RUNBOOK.md sections D and E (gate.sh, the editor, apply_verdict, publish.sh). `--lead <id>` when the biggest story of the front-page check is not the lead (refresh_home.py replaces a held, over-8-hour, clock-stale or markets lead by itself); `--pin <id> ...` for BIG STORIES. Every headline must differ from last hour's: refresh_home.py does this by itself; a nation- or world-changing story stays only when this run added new facts to it (new `updated:`) and passes it with `--critical <id>`, or as a new development story. During a big election count, update content/data/results.json every run from sources read in this run (`active: false` 48 hours after counting ends).
Run name for the lock and the record: `hourly-HH`, HH the hour the run started. Message the owner (SendUserMessage) only when a story was held or the site could not be deployed.
