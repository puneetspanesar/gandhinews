# Long-form run (6:35 am IST only, owner November 16: the evening run and the editorials inside writing runs are stopped)

Owner, November 16: ONE explainer, ONE editorial and ONE fact check per run, each the strongest available (see the top of RUNBOOK.md). Never explain or argue a subject we explained or argued in the last 7 days; update that piece instead if the news moved.

Read newsroom/RUNBOOK.md first: its rules (A), setup (B), pictures (C), gate (D) and publish (E) are part of this runbook. This run writes explainers, editorials and fact checks, and updates the trackers. It does not write news and does not choose the homepage lead; refresh_home.py picks its pieces up for the explainer and opinion slots.

## Time budget (minutes from the start)
- 0 to 6: setup, held stories. (No lock until publish.sh: hourly runs keep publishing while this run works.)
- 5 to 30: desks.
- 30 to 50: pictures. Picture deadline 50: a piece without a correct main picture is held.
- 50 to 70: refresh_home, gate.sh, editor, apply_verdict, gate.sh again if anything was held or fixed, publish.sh.

## 1. Desks (three agents in ONE message, each with `model: "sonnet"`; the editor agent stays on the default model)
Write /home/claude/gn-work/window.txt: the date and time now, the window (since the last "Long-form" commit), and these limits, which override every brief: "LONG-FORM run. Explainers 700 to 1,100 words with 3 in-story visuals; editorials 500 to 800 words with 1 or 2." Each prompt starts `Read /home/claude/gn-work/run-brief.md and follow it. DESK = <desk>.`:
1. explained: 1 explainer on the biggest news of the window not yet explained (check content/en/explainer first; shape of content/en/explainer/at1-bonds-explained-yes-bank-supreme-court-ruling.md). At most 10 WebSearch calls.
2. opinion: 1 editorial on the biggest issue of the window with no editorial yet (check content/en/editorial; shape of content/en/editorial/school-buildings-need-safety-audits-before-the-next-roof-falls.md). At most 8 WebSearch calls.
3. data-and-fact-check: one fact check EVERY run: the most widely shared checkable claim of the last 24 hours by a politician, official or viral post, checked against primary sources only (official documents, data releases, court orders, the original video); never two; update the trackers (content/data/bills.json, sc-cases.json, budget-promises.json, election-calendar.json, parliament-sessions.json and their Hindi twins) where the window changed them. At most 10 WebSearch calls.
Explainers carry 3 in-story visuals, editorials 1 or 2. Then `python3 newsroom/scripts/audit.py --new --skip photos,home,site,style` must pass, and commit locally.

## 2. Pictures
RUNBOOK.md section C, tag `l<day><m|e>`. Explainers and editorials show the place, institution, object or person the piece is about; two pieces of the same run never share a picture, and none reuses a picture from the last 48 hours. An infographic cover only under rule 11.

## 3. Gate, editor, publish
RUNBOOK.md sections D and E. Run name `longform-m` or `longform-e`. Commit message "Long-form morning|evening: N pieces ...". Message the owner only when a piece was held or the site could not be deployed.
