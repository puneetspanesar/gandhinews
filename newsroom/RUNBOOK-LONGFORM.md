# Long-form run (6:35 am and 5:35 pm IST)

Read newsroom/RUNBOOK.md first: its rules (A), setup (B), pictures (C), gate (D) and publish (E) are part of this runbook. This run writes explainers, editorials and fact checks, and updates the trackers. It does not write news and does not choose the homepage lead; refresh_home.py picks its pieces up for the explainer and opinion slots.

## Time budget (minutes from the start)
- 0 to 5: setup, lock (`take longform-m 80` or `longform-e`; if an hourly run holds it, `lock.sh wait` up to 25 minutes), held stories.
- 5 to 30: desks.
- 30 to 50: pictures. Picture deadline 50: a piece without a correct main picture is held.
- 50 to 70: gate, editor, apply_verdict, gate again, publish. Release the lock by minute 75: the hourly run needs it.

## 1. Desks (three agents in ONE message)
Write $GN_WORK/window.txt: the date and time now, the window (since the last "Long-form" commit), and "This is a LONG-FORM run." Each prompt starts `Read /home/claude/gn-work/run-brief.md and follow it. DESK = <desk>.`:
1. explained: 2 explainers on the biggest news of the window not yet explained (check content/en/explainer first; shape of content/en/explainer/at1-bonds-explained-yes-bank-supreme-court-ruling.md). At most 10 WebSearch calls.
2. opinion: 2 editorials on issues of the window with no editorial yet (check content/en/editorial; shape of content/en/editorial/school-buildings-need-safety-audits-before-the-next-roof-falls.md). At most 8 WebSearch calls.
3. data-and-fact-check: one fact check when a widely shared claim of the window can be checked against primary sources; update the trackers (content/data/bills.json, sc-cases.json, budget-promises.json, election-calendar.json, parliament-sessions.json and their Hindi twins) where the window changed them. At most 10 WebSearch calls.
Explainers carry 3 in-story visuals, editorials 1 or 2. Then `python3 newsroom/scripts/audit.py --changed --skip photos,home,site,style` must pass, and commit locally.

## 2. Pictures
RUNBOOK.md section C, tag `l<day><m|e>`. Explainers and editorials show the place, institution, object or person the piece is about; two pieces of the same run never share a picture, and none reuses a picture from the last 7 days. An infographic cover only under rule 11.

## 3. Gate, editor, publish
RUNBOOK.md sections D and E. Run name `longform-m` or `longform-e`. Commit message "Long-form morning|evening: N pieces ...". Message the owner only when a piece was held or the site could not be deployed.
