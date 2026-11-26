# Edition run (6:42 am and 5:42 pm IST; run names hourly-07 and hourly-18)

Read RUNBOOK.md first. Its top section, "The relaunched edition", wins over everything, including this file's older neighbours. Nobody is watching: never stop to ask a question. Decide, note the decision in the run record, carry on.

## 1. Setup
`source /home/claude/gandhinews/newsroom/scripts/setup.sh hourly-07` (or `hourly-18`). Every shell call starts fresh, so use full paths. Count the English pieces already published today (`published:` dated today in content/en) and stay within 8 for the day.

## 2. Choose 3 to 4 pieces (15 minutes at most)
Look at what official India did since the last run: Supreme Court and High Court judgments and orders, Election Commission orders and press notes, PIB releases, Gazette notifications, Parliament business, RBI and ministry data, state government orders. Then check what people are searching for and arguing about today. Choose the pieces where we can add what a reader cannot get elsewhere: what the document actually says, the number in context, the history, what happens next.

- Morning run: 1 or 2 explainers on a question in today's news, 1 news story, and a fact check when a checkable claim is doing the rounds.
- Evening run: 1 or 2 news stories on the day's decisions, 1 explainer or fact check, and the tracker check (RUNBOOK.md, relaunch section).
- Spread the day across sections; do not put more than two pieces a day in one section unless the news demands it.
- Before choosing, search content/en for the subject. Update the existing piece if we have one.

## 3. Write
One piece at a time, yourself or with desk agents given the brief for that format in newsroom/briefs (ignore anything in a brief about sports, science or Parliament sections, the hourly homepage or markets). Each piece: the official source opened and read, quoted exactly and linked, `primary: true`; at least two other sources; `seo.title` of at most 60 characters; `section:` from the seven; the Hindi version written for Hindi readers with every fact, figure and quote of the English one. Explainers answer the question in the first two sentences (`shortAnswer`). Fact checks follow the method on /fact-check/methodology/.

## 4. Pictures
RUNBOOK.md section C. Every piece gets a picture; the piece that will lead gets a photograph, never a graphic.

## 5. Gate, editor, publish
RUNBOOK.md sections D and E: `bash /home/claude/gandhinews/newsroom/scripts/gate.sh`, the editor agent on every new piece, `apply_verdict`, the gate again if anything was held or fixed, then `bash /home/claude/gandhinews/newsroom/scripts/publish.sh hourly-HH "<summary>"`. A piece that fails is held; the rest are published. Then check the live front page and each new piece in both languages.

## 6. Report
ONE short SendUserMessage to Puneet: "Gandhi News, <morning or evening> edition, <date>", then one line per new piece (format, section, headline), any tracker updated, any piece held and why, and any factual conflict or judgement call. If nothing could be published, say exactly why.
