# Desk brief v2: LokVox as a general news site (overrides content-spec.md and desk-addendum-12oct.md where they differ)

LokVox is now a full news site: India, world, science and technology, sports. It must read like a quality newspaper (think BBC, The Hindu, Guardian), not a fact-checking or data site.

## Tone and shape
- Write news the way a good newspaper does: strong news lead, then the people, the scene, what was said, why it matters, what happens next. Narrative paragraphs, not stacks of numbers.
- Use quotes from the people involved (exact words found in sources, with name and role).
- Do not over-hedge. State what happened plainly and confidently when sources agree. Keep "reportedly" only for genuinely single-source or contested claims.
- Never write "fact", "facts", "verified", "fact check", "the record shows", "we checked" or similar in the copy.
- Blocks (chart, facts, infographic, timeline, compare) are OPTIONAL and rare: at most ONE per story, and only when it truly helps (a sports scorecard or points table, a launch timeline). Many stories should have none.
- Length: 400-650 words for news. Sections with H2 subheads are fine but keep them natural (e.g. "How the match turned", "What the mission will do").
- `keyPoints`: 3 bullets, one short sentence each, one key phrase in `**bold**`.

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
- Each story's hero.suggested_source must be a Wikimedia Commons search phrase specific to that story (named person, building, place, team, object). It will be used automatically to find the photo.
