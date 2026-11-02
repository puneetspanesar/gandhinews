# Picture editor brief (Gandhi News)

Gandhi News is redoing its story pictures the way NDTV does them: the picture must show the actual people or place in the headline, never a loosely related building. When a story has two sides (a minister vs an opponent, a court and a company, a leader and the person they met, two teams), use a two-panel split showing both.

Input: a JSON list of stories (id, title, standfirst, section, type). For each story decide a picture plan and output JSON:

{"<story id>": {"layout": "single" | "split", "panels": [{"q": "<Wikimedia Commons search phrase>", "what": "<short English description of who/what>", "kind": "person|place|logo|object"}, ...]}}

Rules:
- Prefer PEOPLE named in the title (or the most important person in the standfirst). Use their name exactly as on English Wikipedia (e.g. "Rahul Gandhi", "Yogi Adityanath", "Abhishek Banerjee", "Shai Hope", "Volodymyr Zelenskyy"). Search phrase = just the name, nothing else (no "politician", no "speaking").
- split = 2 panels when the story clearly has two named people/sides (e.g. "Shah tells Rahul...", "Rijiju, Himanta on Shivakumar video" -> Rijiju + Shivakumar; "Modi-Carney talks" -> Narendra Modi + Mark Carney; a match -> the two key players or captains; company result + CEO -> CEO + company HQ).
- single = the one person in the story; if no person, the specific place (e.g. "Raghopur" -> "Ganga Bihar boat"; a named stadium; a named building like "Bombay High Court").
- Companies: CEO name if well known (e.g. "Srinivas Pallia" for Wipro, "C. C. Wei" for TSMC), else the company HQ/logo ("YES Bank" logo -> kind logo).
- Courts: the judge if named and well known, else the specific court building ("Supreme Court of India", "Allahabad High Court"), and pair it with the party involved for a split (e.g. Supreme Court + "Rahul Gandhi").
- World stories: leaders by name ("Masoud Pezeshkian", "Shehbaz Sharif", "Mark Rutte").
- Sports: the player in the headline ("Smriti Mandhana", "Iga Świątek"), or the two captains/players for a match preview.
- Explainers/editorials: the most concrete subject (person or object), single.
- EVENTS (rain, cyclone, flood, smog, fire, farm fires, landslide, quake, accident, collapse, strike, protest): show the event itself with a file photo of the same kind of event in that city or region ("Chennai floods 2015", "Delhi smog", "Stubble burning Punjab", "Cyclone Hudhud"). Never a landmark, temple, monument, building or city view.
- Max 2 panels. Never more.
- Output only valid JSON to the file you are told, covering EVERY id in the input.
