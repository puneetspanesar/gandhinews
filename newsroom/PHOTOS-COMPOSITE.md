# Two-person splits, in-story photo rounds and covers (the long photo procedure)

Use this only when RUNBOOK.md section C is done and there is time before the picture deadline: two-panel splits (a story with two named sides), many in-story photos, or 16:9 covers. Main pictures come first, always through section C. The query files this writes go in $GN_WORK, never in the repo: the finder takes queries through photos_gh.py, not through pushed files.

```
cd /home/claude/gandhinews/newsroom/scripts && python3 make_plan.py <tag>
```
Use a fresh tag each run (e.g. `m17` for the morning of the 17th, `e17` for the evening). The plan also holds every in-story ```photo block as its own single-panel entry `<story id>--p<n>`; they go through the same finding, picking, eye check, register and composite steps as main photos, and the same never-a-wrong-person rule applies. It writes plan.json and vq.json into gn-work and query files, and prints the parts. For each part run `python3 newsroom/scripts/photos_gh.py find <part> <that part's query file>` (they can run in parallel), which unpacks into $GN_WORK/pcv<part>. Then:
```
cd /home/claude/gn-work && $PY pick.py
```
For panels still missing, write a second round of better queries (official forms like "Shri Rajnath Singh", plain city or building names, `||20` for big pools) into $GN_WORK/q-<tag>r.json with keys like `<tag>r0`, run `photos_gh.py find <tag>r` on it, and map each missing panel query to its new query texts in gn-work/extra.json: `{"Bhagwant Mann": ["Bhagwant Mann Punjab"]}`. Rerun `$PY pick.py`. One extra round is enough.

Review: `$PY review_sheet.py picks`, then Read every ps*.jpg. For each story check every panel shows the named person or the actual place. Remove wrong panels by editing gn-work/picks.json (set the panel to null). Add the file name of every wrong-person or wrong-place pick (lower case, as in the URL, underscores) to newsroom/scripts/blocklist.txt so no later run picks it again. Common failures: a namesake (wrong person with the same surname), a group photo where the person is tiny, a signature or map instead of the person, a logo that is not the company, an unrelated building. When two or more people are in a photo and the crop could land on the wrong face, drop it unless a focus point fixes it. Then list every story still without a picture (no entry in content/photos.map.json and none in picks.json). For each, write two or three fallback queries (institution, place, concrete object, `||15`), run one more finder round, open the candidate sheets (`python3 sheet.py pcv<part> /home/claude/gn-work <tag>` then Read the jpgs), and choose by eye. Add choices by hand to picks.json using a candidate from the pools (fields q, dir, key, n, title, url (=url1600), page, licence, author, kind, what).

In-story photos are different from main photos in one way: when one still has no correct picture after the fallback round, do NOT hold the story; delete that ```photo block from both language files instead (the story keeps its other visuals). If that leaves a story with no in-story visual at all, note it in the report.

Alt text: `python3 register.py`. If it lists stories that need alt text (panels changed from the plan), write gn-work/alts-override.json `{"id": ["English alt", "Hindi alt"]}` naming who or what is actually shown, then run it again. Then:
```
cd /home/claude/gandhinews && npm run -s check:photos
```
It must pass; if it reports a photo repeated too soon, null that panel in picks.json, restore content/photos.json with `git checkout content/photos.json`, and register again. Then download exactly the registered ids (register.py prints them; composite parts are cx-*): `python3 newsroom/scripts/photos_gh.py download <tag> <id> <id> ...`, which unpacks into $GN_WORK/raw-<tag>. Build the composites from that folder:
```
echo '{}' > /home/claude/gn-work/focus.json
$PY /home/claude/gn-work/apply_composites.py /home/claude/gn-work/raw-<tag> /home/claude/gn-work/focus.json | grep -v "^missing parts"
$PY /home/claude/gn-work/review_sheet.py final
```
Then the covers (system python3, which has rembg):
```
cd /home/claude/gandhinews && python3 newsroom/scripts/make_cover.py /home/claude/gn-work/raw-<tag>
```
It makes a 16:9 cover (English and Hindi) for every story with a `cover:` block whose pictures are in. A clean single-person photo is cut out; a group photo or a close-up goes in a white frame using the checked crop; both people in a face-off are treated the same. Read every new public/photos/c-*-en-1280.jpg and c-*-hi-1280.jpg: right person, face clear of the headline, no ghosted or jagged cut-out, headline spelled right and true to the story. A bad cover is never published: fix the `cover:` block and rerun for that id (`make_cover.py <raw> <id>`), or delete the story's `cover` key from content/photos.map.json so it shows its plain picture, and note it in the report.

Read every out*.jpg. If a crop misses the face, add a focus entry `{"story-id": [[fx, fy]]}` (0 to 1 per panel; a third value tightens) and rerun apply_composites. For a logo panel use "fit". If a picture is still wrong, remove the story's entries from content/photos.json and content/photos.map.json and delete its public/photos/v-<id>-*.jpg files.

