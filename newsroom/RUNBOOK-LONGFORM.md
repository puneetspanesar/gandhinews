# Gandhi News long-form run (twice a day): runbook

Runs twice a day (morning and evening, IST). It writes editorials, explainers and other long forms, and refreshes the trackers and data pages. News stories and the homepage are the hourly run's job (RUNBOOK-HOURLY.md); this run only adds its pieces, and the next hourly run puts them on the homepage. Work alone: never stop to ask a question. Decide, note it in the report, carry on.

Everything in RUNBOOK.md "Standing editorial rules" applies.

## 0. Lock and set up
Same lock as RUNBOOK-HOURLY.md step 0, but if the lock is held, wait (check every 2 minutes, up to 25 minutes) instead of stopping; take it with `lock "busy <time> longform"`. Then RUNBOOK.md step 0. Window: since the last "Long-form update" commit.

## 1. Desks (in parallel, ONE message)
1. explained: 2 explainers (shape of content/en/explainer/at1-bonds-explained-yes-bank-supreme-court-ruling.md) on the biggest news of the window not yet explained. Check content/en/explainer first. Max 10 WebSearch calls.
2. opinion: 2 editorials (shape of content/en/editorial/school-buildings-need-safety-audits-before-the-next-roof-falls.md) on issues of the window that have no editorial yet. Check content/en/editorial first. Max 8 WebSearch calls.
3. data-and-fact-check: one fact check when a widely shared claim from the window can be checked against primary sources; update the trackers (content/data/bills.json, sc-cases.json, budget-promises.json, election-calendar.json, parliament-sessions.json and their Hindi twins) where the window changed them. Max 10 WebSearch calls.
Then validate and commit as RUNBOOK.md step 1 says.

## 2. Pictures
RUNBOOK.md step 2 with tag `l<day><m|e>`. Explainers and editorials take a picture of the place, institution or object the piece is about when there is no single person; never a wrong person. Pieces still without a correct picture move to newsroom/held/ and are named in the report.

## 3. Build, publish, report
RUNBOOK.md step 4. Commit "Long-form update <morning|evening>: N pieces", push, then release the lock. When the Cloudflare build has finished, run `npm run -s indexnow -- 13`. Send one short SendUserMessage: what was written (titles), anything held or doubtful. No em dashes.
