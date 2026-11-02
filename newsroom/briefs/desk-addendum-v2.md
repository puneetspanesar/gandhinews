# Desk brief v2: Gandhi News as a general news site (overrides content-spec.md and desk-addendum-12oct.md where they differ)

Gandhi News is now a full news site: India, world, science and technology, sports. It must read like a quality newspaper (think BBC, The Hindu, Guardian), not a fact-checking or data site.

## Tone and shape
- Write news the way a good newspaper does: strong news lead, then the people, the scene, what was said, why it matters, what happens next. Narrative paragraphs, not stacks of numbers.
- Use quotes from the people involved (exact words found in sources, with name and role).
- Do not over-hedge. State what happened plainly and confidently when sources agree. Keep "reportedly" only for genuinely single-source or contested claims.
- Never write "fact", "facts", "verified", "fact check", "the record shows", "we checked" or similar in the copy.
- Bold the key phrase in the body text. In most paragraphs, wrap the one phrase that carries the news in `**bold**`: the number, the decision, the result, or a name with what they did (2 to 7 words, e.g. "the court **stayed the order for four weeks**"). At most one per paragraph, never a whole sentence, never inside a quote, and skip paragraphs with nothing worth it. The reader should get the story by reading only the bold. Same in the Hindi twin.
- Visuals inside the story. Besides the main photo, every story carries more visuals in the body: briefs 2, leads and explainers 3, editorials 1 or 2. Spread them through the story where they help the reading (after the paragraph they illustrate), never stacked together and never right at the top.
  - Photos (```photo blocks) are the default. Each shows a DIFFERENT person, place or thing than the main photo, one the story actually talks about: the other side in a dispute, the minister who announced it, the court, the venue, the stadium, the site of the incident, the spacecraft. Format: three lines, the opening fence ```photo on its own line, then the JSON on one line {"n":1,"subject":"<Wikimedia Commons search phrase: a person's name exactly as on English Wikipedia, or a specific named place or object>","caption":"<one sentence saying who or what it is and why it is in the story>","alt":"<who or what is shown>"}, then the closing ``` on its own line (a one-line block is not picked up by the photo finder). Number them 1, 2, 3 in order. The Hindi twin repeats the same blocks with the same n and subject, and a Hindi caption and alt. Never pick a subject that is generic ("Indian flag", "stock market", "cricket ball") or that could only be found as a logo. In an event story the in-story photos show the event too (more rain, flooding, rescue teams, the storm), never a landmark or a building.
  - Infographics (chart, facts, timeline, compare, infographic blocks) only when the story has something worth drawing: a real series of numbers (a chart), a run of dated events (a timeline), two sides or before and after (compare), or three or four key figures (facts or infographic). Never a chart of one or two numbers, never a block that repeats the keyPoints, never one just to fill the slot. Most stories will have no infographic and use photos instead; a story with real data might have one infographic and one or two photos. At most one chart per story.
- Length: 400-650 words for news. Sections with H2 subheads are fine but keep them natural (e.g. "How the match turned", "What the mission will do").
- `keyPoints`: 3 bullets, one short sentence each, one key phrase in `**bold**`.

## Cover (every news story, leads and briefs)
Every story gets a 16:9 cover: the people in the story placed over a picture of the scene, a red label, a short cover headline and our mark. It is used on the homepage, at the top of the story and when the story is shared. Add a `cover:` block to the front matter (English), and the same block in the Hindi twin with Hindi `label`, `headline` and data labels:
```
cover:
  template: faceoff     # faceoff: one person against another (both in hero.subjects) | speaker: one person's words or act | breaking: big world or national news | sport: a match or player | business: numbers, sales, markets
  label: "CEC row"      # 1 to 3 words: the running story, or BREAKING only when it truly broke in the last hours
  headline: "'Modi's life is in Gyanesh Kumar'"   # about 40 characters, 2 lines at most: the strongest REAL line (an exact quote in single quotes, or the plain fact). No clickbait, no question, nothing not in the story
  bg: "Ramlila Maidan"  # Wikimedia Commons search for the scene behind the people: the venue, the court, the ship, the stadium; for an event, the event itself ("Chennai floods", "Delhi smog"). Never a landmark or city view, never generic ("crowd", "flag")
  inset: "Iran Ministry of Foreign Affairs"   # breaking only, optional: a second place or object shown in a small circle
  people: ["Abbas Araghchi"]   # only when the main picture is a place or object: the person(s) the story is about, for the cover
  score: ["NZ 192/3", "IND 191/8"]            # sport only, when there is a result
  data: [{icon: trend-up, value: "2.24 lakh", label: "e-two-wheelers registered in October"}]   # business only, 2 or 3 real figures from the story; icons from src/icons
```
The people are hero.subjects (speaker or actor first). Never invent a quote, a figure or a scene for the cover.

## Still required
- Accuracy: every name, number, date and quote must come from a source you actually read (WebSearch / WebFetch). If you can't confirm it, leave it out. Note doubts in `verification.notes` (internal only).
- Own voice: never attribute to media outlets in the body text ("Reuters reported", "told ANI"). Attribute to people and bodies.
- No em dashes anywhere. Indian English spellings. ₹, lakh/crore for Indian money; for foreign money use $ or the local currency as reported.
- Today is Saturday 17 October 2026, about 6 pm IST. Cover news from late Friday night and Saturday that is not on the site yet. Anything scheduled for Sunday 18 October or later is a preview.
- Frontmatter as in content-spec.md, with: `type: news`, `verification.status: approved`, `hero` with `need`, `suggested_source` (a Wikimedia Commons search term likely to find a freely licensed photo), `alt`, and `overlay: { value: "max ~40 characters" }`. No sources field shown to readers is needed beyond the frontmatter list (official documents `primary: true`, media `primary: false`).
- Sections: `world` (global news), `science` (science and technology), `sports`. format_label like "World / Middle East", "Science & Tech / Space", "Sports / Cricket"; Hindi: "दुनिया / पश्चिम एशिया", "विज्ञान-तकनीक / अंतरिक्ष", "खेल / क्रिकेट".
- `topics: []` is fine. `related`: only ids that exist (ls /home/claude/gandhinews/content/en/*/).
- Write the Hindi adaptation too at content/hi/news/{slug}.md (`translation_of: {slug}`, same id), natural Hindi news register (see /home/claude/gn-work/hindi-glossary.md), own Hindi headline, standfirst, keyPoints, overlay and seo.
- Validate YAML: python3 -c "import yaml,sys;[yaml.safe_load(open(f).read().split('---')[1]) for f in sys.argv[1:]]" FILES
- Block JSON formats if you use one: chart {"type":"hbar|vbar|line","title":"...","unit":"","data":[{"label":"..","value":1}]}; timeline {"title":"..","items":[{"date":"..","text":".."}]}; infographic {"title":"..","items":[{"icon":"<phosphor name that exists in /home/claude/gandhinews/src/icons>","value":"..","label":"..","text":".."}]}.
- Photos: never reuse a photo already used by another story (check content/photos.map.json). Suggest a Commons search term specific to THIS story (the person, place or object in it). Run `npm run check:photos` before every push; it must pass.
- Volume run rules: you are one of ~12 desks writing ~70 stories in this run. BEFORE writing each story, check /home/claude/gn-work/claims.txt (other desks' claimed stories) and `ls content/en/news`; if the event is already claimed or published, pick another. Then append one line `slug | desk | one-line topic` to claims.txt (use `echo ... >> claims.txt`). Never write a story already on the site unless told to update it.
- Mix of lengths: lead stories 400-650 words; briefs 220-380 words (still with keyPoints, a proper lead, quotes where available). Briefs are fine for smaller items.
- Each story's hero.suggested_source (and each photo block's subject) must be a Wikimedia Commons search phrase specific to that story (named person, building, place, team, object). It will be used automatically to find the photo.
