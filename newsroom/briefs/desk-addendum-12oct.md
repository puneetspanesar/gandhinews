# Desk addendum (overrides content-spec.md where they differ)

- The site is **Gandhi News** (gandhinews.com).
- The current date and time come from `TZ=Asia/Kolkata date` at the start of the run. Write as of now. Events later today have NOT happened: write them as planned ("is due to", "will"), never as done.
- **Own voice.** In the body text, do NOT attribute to media outlets ("PTI reported", "according to The Hindu", "told ANI"). Attribute claims to the people or bodies who made them ("the MEA said", "Congress general secretary K C Venugopal said on October 10"). Facts that rest on media reports are stated plainly if two sources agree, or hedged ("police were reported to have...") if only one; record which outlet in `verification.notes`.
- Fact boxes, charts, timelines: NO "source" field shown. Omit the `source` key in chart/facts JSON.
- `sources` frontmatter: list everything you used (internal record). Mark official documents (PIB, ministry, RBI, court orders, company filings to BSE/NSE, MEA statements on mea.gov.in) `primary: true`; media `primary: false`.
- `keyPoints`: 3-4 bullets, each with exactly ONE key fact wrapped in `**bold**` (rendered red).
- `hero` must include `overlay: { value: "..." }`: a short (max ~45 characters) punchy factual phrase related to the story, shown on the photo. Hindi file gets its own Hindi overlay value.
- `verification.status: approved` (the editor has approved this batch); list doubts in `verification.notes`.
- Quotes: only exact words found in a source, with speaker, role and date. Paraphrase otherwise.
- Bylines are automatic; do not add any.
- Infographic block available (use where useful, besides chart/facts/timeline):
  ```infographic
  {"title":"...","items":[{"icon":"users","value":"7,000+","label":"short label","text":"one sentence"}]}
  ```
  icons are Phosphor names (users, scales, buildings, ship, airplane, chart-line, currency-inr, truck, train, megaphone, gavel, newspaper, map-pin, warning, handshake, globe, briefcase, cpu, bank).
  Compare block (columns/rows schema):
  ```compare
  {"title":"...","columns":["Col A","Col B"],"rows":[{"icon":"users","label":"Row","cells":["a","b"]}]}
  ```
- Hindi version: write a full Hindi adaptation at content/hi/news/{slug}.md with `translation_of: {slug}`, same id/slug, same facts, Hindi format_label (e.g. "राजनीति / विपक्ष"), Hindi title/standfirst/keyPoints (with one **bold** each)/seo/overlay. Follow /home/claude/gn-work/hindi-glossary.md. Sources list identical (English titles OK).
- `related`: only ids that exist in content/en (check with ls). Topics: only ids from spec section 5, or existing topic files in content/en/topic.
- After writing, run `cd /home/claude/gandhinews && npx astro check 2>/dev/null | tail -3` is NOT needed; instead run `node -e` free. Just make sure YAML is valid: `python3 -c "import yaml,sys;[yaml.safe_load(open(f).read().split('---')[1]) for f in sys.argv[1:]]" FILES`.
- No em dashes anywhere, in either language.
