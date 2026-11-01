# Gandhi News scheduled news update: runbook

This is the full procedure for one news update of gandhinews.com. It runs twice a day (about 5:30 am and 3:30 pm IST) so the site is fresh by 7 am and 5 pm. Work alone: nobody is watching, so never stop to ask a question. Decide, note the decision in the final report, and carry on.

The site is Astro in the private repo puneetspanesar/gandhinews. Cloudflare Workers Builds deploys every push to main. Work on main directly.

## Standing editorial rules (never break)
- Byline is "From the editorial desk". Write in our own voice; never quote or credit media outlets to readers (sources stay in front matter only).
- Key facts in keyPoints are wrapped in **bold** (they render bold red). In the body, most paragraphs bold the one phrase that carries the news (at most one per paragraph, never a whole sentence).
- Besides the main photo, every story carries 2 or 3 visuals in the body (briefs 2, leads and explainers 3, editorials 1 or 2): mostly in-story photos (```photo blocks, each a different person or place from the story), with an infographic only when there is real data, a sequence or a comparison worth drawing. Never charts for the sake of it. Rules in newsroom/briefs/desk-addendum-v2.md.
- No em dashes anywhere, English or Hindi.
- Every story has its Hindi twin in content/hi/<same folder>/<same slug>.md.
- Never repeat a photo file across stories (`npm run check:photos` must pass).
- Pictures show the actual people or place in the headline (NDTV style), two panels when the story has two sides. EVERY story must go live with a picture (the owner checks). A wrong person is never acceptable, so when the exact person has no usable photo, fall back in this order: another person named in the story; the institution or place (the court, ministry, bank HQ, stadium, city); a concrete object of the story (a crop field, an oil tanker, a satellite). Never publish a run with stories still missing pictures.
- Prefer official government photos (PIB) where Commons has them.
- No "Latest" timestamp section on the homepage. Fact-check, trackers, data desk, Parliament table, standards box stay at the bottom.
- Volume: about 70 to 80 stories per run, two thirds briefs (220 to 380 words), one third leads (400 to 650 words).

## 0. Set up the workspace (fresh session)
```
[ -d /home/claude/gandhinews/.git ] || gh repo clone puneetspanesar/gandhinews /home/claude/gandhinews
cd /home/claude/gandhinews && git pull -q && npm ci --silent
mkdir -p /home/claude/gn-work && cp newsroom/briefs/*.md newsroom/scripts/*.py newsroom/scripts/blocklist.txt /home/claude/gn-work/
[ -x /tmp/claude-0/cvenv/bin/python ] || (python3 -m venv /tmp/claude-0/cvenv && /tmp/claude-0/cvenv/bin/pip -q install "opencv-python-headless<5" pillow numpy pyyaml)
: > /home/claude/gn-work/claims.txt
```
Set `PY=/tmp/claude-0/cvenv/bin/python`. Work out the window: from the last news-run commit (`git log --format='%ci %s' -15`) to now (`TZ=Asia/Kolkata date`).

## 1. Brief the desks
Edit three lines in /home/claude/gn-work:
- desk-addendum-v2.md, the line starting `- Today is`: the day, date and time now, what period to cover (since the last run), and that later events are previews.
- run-brief.md line 1 (title) and the `- News from ...` volume rule: the same window; tell desks to `ls -t content/en/news | head -150` to avoid repeats.
- run-brief.md `published:` rule: ISO times inside the window (+05:30).

Then launch nine desk agents in ONE message (Agent tool, general-purpose, run in parallel). Each prompt starts `Read /home/claude/gn-work/run-brief.md and follow it. DESK = <desk>. Section: <section>.` then two or three lines of what to cover for this window, then a target:
1. politics-courts (politics/policy): national politics, EC/SIR, parties, Supreme Court and High Court orders. 9 stories (3 leads).
2. states: at least 6 different states, Delhi air quality with CPCB AQI. 10 (3 leads).
3. economy: market close on weekdays as a lead AND update content/data/economy-dashboard.json and content/data/hi/economy-dashboard.json (read first, keep structure, add history rows, set "updated"); results, IPOs, RBI/SEBI. Morning runs: overnight global cues and the day's results calendar instead of a close. 9 (3 leads). Report dashboard values.
4. policy (policy/parliament): PIB releases, ministries, MEA, defence, regulators. 8 (2 leads).
5. world-asia (world): Gulf/Iran, Israel/Gaza, Pakistan, Bangladesh, Nepal, China, East and Southeast Asia. India angles. 9 (3 leads).
6. world-west (world): Europe, Russia-Ukraine, US, Latin America, Africa, UN. 8 (2 leads).
7. science: AI and tech, Indian tech policy, space, health, climate. At least 3 India angles. 7 (2 leads).
8. sports: cricket first (India men and women, domestic), then other Indian interest, then global. 10 (3 leads).
9. explained-opinion: 3 explainers (copy the shape of content/en/explainer/at1-bonds-explained-yes-bank-supreme-court-ruling.md) on this week's news not yet explained, and 2 editorials (shape of content/en/editorial/school-buildings-need-safety-audits-before-the-next-roof-falls.md) on issues without one. Check the folders first. Limit WebSearch to 10. Morning runs may do 1 explainer and 1 editorial.

Wait for all nine. Then validate:
```
cd /home/claude/gandhinews && rm -rf node_modules/.astro .astro/data-store.json && npm run build 2>&1 | grep -iE "error|Indexed [0-9]+ pages"
```
Fix any error (common: duplicate front matter keys, explainer compare block in the old left/right shape, unknown icon names; see src/icons for valid ones). Skim the headlines of the new stories for anything unsourced or doubtful and fix or delete it (delete both language files). Commit and push the stories now (`git add content && git commit`), so a later failure never loses them. End every commit message with the attribution lines given in the session's system reminder.

## 2. Pictures
```
cd /home/claude/gandhinews/newsroom/scripts && python3 make_plan.py <tag>
```
Use a fresh tag each run (e.g. `m17` for the morning of the 17th, `e17` for the evening). The plan also holds every in-story ```photo block as its own single-panel entry `<story id>--p<n>`; they go through the same finding, picking, eye check, register and composite steps as main photos, and the same never-a-wrong-person rule applies. It writes plan.json and vq.json into gn-work and scripts/photo-queries-<tag>N.json, and prints the parts. Commit and push the query files, then trigger one finder run per part:
```
gh api -X POST repos/puneetspanesar/gandhinews/actions/workflows/find-photos.yml/dispatches -f ref=main -f "inputs[part]=<part>"
```
Poll `gh run list --workflow find-photos.yml -L <n> --json status,conclusion` every 30 s until all complete (about 6 to 8 minutes). Fetch the candidates (delete old pcv* folders first):
```
cd /home/claude/gn-work && rm -rf pcv*
for p in <parts>; do git -C /home/claude/gandhinews fetch -q origin +photo-candidates-$p:refs/remotes/origin/photo-candidates-$p && mkdir -p pcv$p && git -C /home/claude/gandhinews archive origin/photo-candidates-$p photo-candidates | tar -x -C pcv$p; done
$PY pick.py
```
The part name you trigger must match a query file that is already pushed (`scripts/photo-queries-<part>.json`, check with `ls scripts/photo-queries-<part>.json && git log origin/main -1 -- scripts/photo-queries-<part>.json`); a wrong or unpushed name fails the finder run and emails the owner. For panels still missing, write a second round of better queries (official forms like "Shri Rajnath Singh", plain city or building names, `||20` for big pools) into scripts/photo-queries-<tag>r.json with keys like `<tag>r0`, push, trigger, fetch into pcv<tag>r, and map each missing panel query to its new query texts in gn-work/extra.json: `{"Bhagwant Mann": ["Bhagwant Mann Punjab"]}`. Rerun `$PY pick.py`. One extra round is enough.

Review: `$PY review_sheet.py picks`, then Read every ps*.jpg. For each story check every panel shows the named person or the actual place. Remove wrong panels by editing gn-work/picks.json (set the panel to null). Add the file name of every wrong-person or wrong-place pick (lower case, as in the URL, underscores) to newsroom/scripts/blocklist.txt so no later run picks it again. Common failures: a namesake (wrong person with the same surname), a group photo where the person is tiny, a signature or map instead of the person, a logo that is not the company, an unrelated building. When two or more people are in a photo and the crop could land on the wrong face, drop it unless a focus point fixes it. Then list every story still without a picture (no entry in content/photos.map.json and none in picks.json). For each, write two or three fallback queries (institution, place, concrete object, `||15`), run one more finder round, open the candidate sheets (`python3 sheet.py pcv<part> /home/claude/gn-work <tag>` then Read the jpgs), and choose by eye. Add choices by hand to picks.json using a candidate from the pools (fields q, dir, key, n, title, url (=url1600), page, licence, author, kind, what).

In-story photos are different from main photos in one way: when one still has no correct picture after the fallback round, do NOT hold the story; delete that ```photo block from both language files instead (the story keeps its other visuals). If that leaves a story with no in-story visual at all, note it in the report.

Alt text: `python3 register.py`. If it lists stories that need alt text (panels changed from the plan), write gn-work/alts-override.json `{"id": ["English alt", "Hindi alt"]}` naming who or what is actually shown, then run it again. Then:
```
cd /home/claude/gandhinews && npm run -s check:photos
```
It must say every photo is unique; if not, null the repeated panel in picks.json, restore content/photos.json with `git checkout content/photos.json`, and register again. Commit, push, and trigger the downloader:
```
gh api -X POST repos/puneetspanesar/gandhinews/actions/workflows/download-photos.yml/dispatches -f ref=main
```
Wait for it to finish, then build the composites:
```
git fetch -q origin +photo-raw:refs/remotes/origin/photo-raw
rm -rf /home/claude/gn-work/raw && mkdir -p /home/claude/gn-work/raw && git archive origin/photo-raw | tar -x -C /home/claude/gn-work/raw
echo '{}' > /home/claude/gn-work/focus.json
$PY /home/claude/gn-work/apply_composites.py /home/claude/gn-work/raw /home/claude/gn-work/focus.json | grep -v "^missing parts"
$PY /home/claude/gn-work/review_sheet.py final
```
Read every out*.jpg. If a crop misses the face, add a focus entry `{"story-id": [[fx, fy]]}` (0 to 1 per panel; a third value tightens) and rerun apply_composites. For a logo panel use "fit". If a picture is still wrong, remove the story's entries from content/photos.json and content/photos.map.json and delete its public/photos/v-<id>-*.jpg files.

## 3. Homepage
Update content/homepage.json (see newsroom/homepage-example.py for a full worked example; write a similar script for this run):
- lead: the biggest story of the window; set lead.live.title (EN and HI, e.g. "Cyclone Arnab") to the running story's short name, which labels the lead and the red live band. lead.relatedBelow feeds the live band (first item is its picture story); with an overlay kicker/value (EN and HI), a 4-item dataBox (icons from src/icons, colours #cc0000, #8f0000, #0d0d0d, #6e6e6e), relatedBelow (2) and relatedBeside (5).
- briefing.items: 8 one-line items across sections, EN and HI. Their short leads ("Cyclone:", "Iran:") also become the running-stories strip under the masthead on every page, so keep them short.
- topStories (big + 2 also + 5 list), startHere (6 explainers), opinion (newest editorials first), sections (politics, economy, states, policy leads/lists), desks (world, science, sports), weekAhead (5 dated items, nearest first, drop past ones).
Every id must exist; the example script checks this.

## 4. Build, check, publish
```
cd /home/claude/gandhinews && npm run -s check:photos && rm -rf node_modules/.astro .astro/data-store.json && npm run build 2>&1 | grep -iE "error|Indexed [0-9]+ pages"
```
Must build with no errors. If a push is rejected because another run pushed first, `git pull --rebase`; if content/photos.json or content/photos.map.json conflict, keep BOTH sides' entries (merge the JSON, never take one side), then rerun `npm run -s check:photos` before pushing. A lost map entry blanks a story's picture on the live site. Optionally screenshot the homepage with Playwright (Chromium is preinstalled) and Read it. Commit (`git add -A content public/photos scripts`), push. Check the deploy went out: the push triggers Cloudflare; nothing else to do.

## 5. Report
Send one short message (SendUserMessage) to the user: how many stories, the lead, anything dropped or doubtful, and pictures still missing. Plain words, no em dashes.
