> OVERRIDES: read /home/claude/gn-work/desk-addendum-v2.md first. Gandhi News is a general news site (India, world, science and tech, sports) written in a newspaper style; it is not a fact-check or data site.

# Gandhi News content spec and style guide (V1)

Gandhi News is an independent Indian news site on politics, policy, the economy and Parliament. It is named after Mahatma Gandhi; its promise is satya (truth). Every story is credited "From the editorial desk". No individual bylines.

Today's date and time: take them from `TZ=Asia/Kolkata date` at the start of the run and write as of then.

## 1. Facts discipline (most important)
- Every fact, figure, date, quote and name must come from a source you have actually read (the research files in /home/claude/gandhinews/research/ or pages you open with WebFetch / WebSearch). Never fill gaps from memory or estimate.
- Prefer primary sources: rbi.org.in, mospi.gov.in, pib.gov.in, prsindia.org, sansad.in, eci.gov.in, indiabudget.gov.in, egazette, court orders, ministry sites. Secondary: The Hindu, Indian Express, Hindustan Times, Mint, Business Standard, Economic Times, Reuters, PTI, LiveLaw, Bar & Bench, Supreme Court Observer. Do NOT rely on exam-prep sites, coaching blogs, vendor blogs, Wikipedia or partisan outlets for any fact; if that is the only source, either find a better one or leave the fact out.
- If sources conflict, use the primary source, or name both sources and their figures ("PRS puts productivity at 15%; the government's figure is 19%").
- Distinguish clearly: happened, announced, proposed, alleged, reported. Attribute allegations and claims to the person or party making them. Never name a media outlet in the text: when a fact rests on one media report, state it with care ("police were reported to have...") and record the outlet in `verification.notes`.
- Quotes: only real quotes found in sources, word for word, attributed with name, role and date. Never invent quotes, sources or "officials said" lines. Never write anonymous quotes.
- Be politically even-handed: present each side's position in its own terms; no loaded adjectives; the editorial view appears only in editorials.
- If a sentence cannot be sourced, delete it. List anything you were unsure about in the frontmatter `verification.notes`.

## 2. Writing style
- Human, plain, confident Indian English (programme, organisation, labour, per cent as "%"). Short paragraphs (2-4 sentences). Lead with the news or the answer.
- NO em dashes anywhere (use commas, colons, full stops or brackets). No en dashes at all: ranges are written "2026-27" or "50 to 75".
- Avoid AI-sounding patterns: no "it's not X, it's Y" / "not just X but Y" contrasts, no "In a world where", "delve", "landscape", "navigate", "pivotal", "crucial", "underscores", "a testament to", "amid growing", "in today's", no repetitive parallel structures ("On X... On Y..."), no rhetorical questions in news, no summary paragraph starting "In conclusion" or "Overall".
- Numbers: Indian system (lakh, crore). ₹ symbol before figures (₹2.04 lakh crore). Percentages with "%". Dates in English always month day, year: "October 11, 2026", "Oct 7" in tables. In Hindi: "11 अक्टूबर 2026". Times as "9:30 am IST".
- Headlines: sentence case, specific, factual, under 90 characters, no clickbait, no colons unless needed.
- Standfirst: one or two sentences (under 220 characters) that add to the headline.

## 3. Formats and lengths
- news: briefs 220-380 words, leads 400-650 (window.txt gives the run's limits). keyPoints (3-4 bullets, each one sentence) in frontmatter. At least one chart or fact box when data exists. Sections with H2 subheads.
- explainer: 700-1,100 words. `shortAnswer` (2-3 sentences) in frontmatter. Body is a series of H2 QUESTIONS (5-8), each answered with a direct first sentence in bold, then detail. Include at least one chart, timeline or fact box. These are evergreen: write so they stay true for months, and note "as of <month> <year>" where figures will change.
- factcheck: 450-700 words. Frontmatter `factcheck` block. Body: "What we found" paragraph, then numbered evidence H3 sections each citing a source, then "Why this claim spread" (only sourced context). Verdict scale: True / Mostly true / Misleading / False.
- editorial: 500-700 words, the desk's argued view, evidence-based, fair to the other side's best argument, ends with a concrete recommendation. Include a "The reporting behind this view" facts block (3 numbers with sources). Frontmatter `verification.status: needs-editor-approval`.
- topic: 300-500 words. A living summary of the subject as of today: what it is, where things stand, key dates (timeline block), key numbers (facts block), "Key questions" (3-5 Q&A, short), and `related` list of article ids.
- tracker: a Markdown page (intro 120-250 words + how to read it + source note) plus a JSON data file in /content/data/ with every data row sourced.

## 4. File format
Path: /home/claude/gandhinews/content/en/{type}/{slug}.md (Hindi later at /content/hi/...). Slug: lowercase, hyphenated, 4-9 words, no dates unless needed.

Frontmatter (YAML):
```
---
id: rbi-raises-repo-rate-to-5-50
lang: en
type: news            # news | explainer | factcheck | editorial | topic | tracker
section: economy      # politics | policy | economy | parliament | states | world
format_label: News    # shown above headline e.g. "Economy / RBI"
topics: [rbi-interest-rates, inflation]
title: "..."
standfirst: "..."
published: 2026-10-07T13:30:00+05:30
updated: 2026-10-11T09:00:00+05:30   # optional
location: Mumbai       # news only, optional
keyPoints:             # news only
  - "..."
shortAnswer: "..."     # explainer only
factcheck:             # factcheck only
  claim: "..."
  claimant: "..."
  seenOn: "..."
  firstSeen: 2026-09-15
  verdict: Mostly true
  finding: "one or two sentences"
hero:
  need: "what photo would suit, e.g. RBI headquarters Mumbai, or Governor at policy press conference"
  suggested_source: "PIB / RBI / Sansad TV / Wikimedia Commons search term or URL if known"
  alt: "..."
related: [other-article-ids]
seo:
  description: "150-160 characters"
sources:
  - title: "..."
    publisher: "..."
    date: 2026-10-07
    url: "https://..."
    primary: true
verification:
  status: draft
  notes:
    - "anything unverified or conflicting"
---
```

Body: Markdown. H2 (##) for sections. Do not repeat the title.

Special blocks (fenced code blocks with a language tag; content is JSON):
```chart
{"type":"hbar|vbar|line","title":"...","subtitle":"... (units)","unit":"%","data":[{"label":"Apr-Jun 2025","value":7.8},{"label":"...","value":8.6,"highlight":true}],"source":"MoSPI, 29 Aug 2026"}
```
```facts
{"title":"...","items":[{"value":"5.50%","label":"repo rate from Oct 7, 2026","source":"RBI"}]}
```
```timeline
{"title":"...","items":[{"date":"Oct 7, 2026","text":"..."}]}
```
Quotes: a Markdown blockquote; final line "Source: Name, role, date". Only real, sourced quotes.

## 5. Topic slugs (use these ids in `topics`)
rbi-interest-rates, inflation, gst, labour-codes, electoral-rolls-sir, election-commission, delimitation, elections-2027, parliament, census-2027, india-us-trade, data-protection, economy, budget-2026-27, supreme-court, states, agriculture-msp, fiscal-deficit, rupee-forex
