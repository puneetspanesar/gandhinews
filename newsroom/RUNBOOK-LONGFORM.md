# Gandhi News long-form run (twice a day): runbook

Runs twice a day (morning and evening, IST). It writes editorials, explainers and other long forms, and refreshes the trackers and data pages. News stories and the homepage are the hourly run's job (RUNBOOK-HOURLY.md); this run only adds its pieces, and the next hourly run puts them on the homepage. Work alone: never stop to ask a question. Decide, note it in the report, carry on.

Everything in RUNBOOK.md "Standing editorial rules" applies.

## 0. Lock and set up
Same lock as RUNBOOK-HOURLY.md step 0, but if an hourly run holds it, wait (check every 2 minutes, up to 25 minutes) instead of stopping; take it with `lock "busy <time> longform"`. Hourly runs do not wait for a longform lock and may push while you work: always `git pull --no-rebase` before pushing and merge photo JSON conflicts (RUNBOOK.md). Never reuse a photo that a live or held news story already uses (check:photos catches this). Then RUNBOOK.md step 0. Window: since the last "Long-form update" commit.

## 1. Desks (in parallel, ONE message)
1. explained: 2 explainers (shape of content/en/explainer/at1-bonds-explained-yes-bank-supreme-court-ruling.md) on the biggest news of the window not yet explained. Check content/en/explainer first. Max 10 WebSearch calls.
2. opinion: 2 editorials (shape of content/en/editorial/school-buildings-need-safety-audits-before-the-next-roof-falls.md) on issues of the window that have no editorial yet. Check content/en/editorial first. Max 8 WebSearch calls.
3. data-and-fact-check: one fact check when a widely shared claim from the window can be checked against primary sources; update the trackers (content/data/bills.json, sc-cases.json, budget-promises.json, election-calendar.json, parliament-sessions.json and their Hindi twins) where the window changed them. Max 10 WebSearch calls.
Every piece bolds its key phrases and carries in-story visuals (explainers 3, editorials 1 or 2), as desk-addendum-v2.md says. Then validate and commit as RUNBOOK.md step 1 says.

## 2. Pictures
RUNBOOK.md step 2 with tag `l<day><m|e>`. Explainers and editorials take a picture of the place, institution or object the piece is about when there is no single person; never a wrong person. Pieces still without a correct picture get an infographic cover from their `infographic:` block (`python3 newsroom/scripts/make_infographic.py <id> ...`), never a wrong photo and never a hold for lack of a picture.

## 2b. Editor's check (never skip; nothing is published until it passes)
After the clean build, and BEFORE the final commit and push:
1. Save the front-page list from step 0b (other sites' top stories, one per line) to /home/claude/gn-work/frontpages.txt.
2. `python3 newsroom/scripts/review_pack.py <ids of this run's pieces>` (it screenshots the built homepage and makes one sheet per story).
3. Launch ONE separate agent (Agent tool, general-purpose, a fresh agent that did none of this run's work) with the prompt: `Read /home/claude/gandhinews/newsroom/briefs/editor-check.md and follow it exactly.` Wait for its reply.
4. If it says FAIL, fix every FIX line (find a correct picture, recrop, rebuild a cover, change the lead or the headline mix), rebuild, rerun review_pack and ask a NEW editor agent again. At most two fix rounds.
5. Anything still failing after two rounds: take that story off the homepage and out of this push (move its files to newsroom/held/), or revert the homepage to the last good homepage.json. Never publish a FAIL.
6. Note the editor's final verdict in the commit message ("editor: PASS" or "editor: PASS after fixes: ...").

## 3. Build, publish, report
RUNBOOK.md step 4, then step 2b, the editor's check, until it passes. Commit "Long-form update <morning|evening>: N pieces", push, then release the lock. When the Cloudflare build has finished, run `npm run -s indexnow -- 13`. Send one short SendUserMessage: what was written (titles), anything held or doubtful. No em dashes.
