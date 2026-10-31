# content/data/markets.json

Feeds the black "Markets and data" band on the homepage (src/components/MarketsBand.astro). One file serves both languages: names carry an optional `name_hi`. Every number must come from a source read in the run that wrote it. Never estimate; when a value can't be found, keep the old value (and the old `session_date`) and say so in the run report.

```json
{
  "as_of": "2026-10-30T15:45:00+05:30",       // when these numbers were read (IST)
  "status": "closed",                          // "open" during 9:15 to 15:30 IST on trading days, else "closed"
  "session_date": "2026-10-30",                // the trading day the numbers belong to
  "chart": "nifty-50",                         // which index the big chart shows
  "indices": [
    { "id": "sensex", "name": "Sensex", "name_hi": "सेंसेक्स", "value": 0, "change": 0, "pct": 0,
      "history": [ { "date": "2026-10-01", "close": 0 } ],   // daily closes, oldest first, last 30 sessions
      "source": "https://..." }
  ],                                           // order shown: Sensex, Nifty 50, Nifty Bank, Nifty Midcap, India VIX (five tiles)
  "rates": [
    { "id": "usd-inr", "name": "Rupee per dollar", "name_hi": "रुपया प्रति डॉलर", "value": 0, "change": 0, "pct": 0, "decimals": 2, "unit": "", "unit_hi": "", "source": "" }
  ],                                           // rupee vs $, €, £; Brent ($/barrel); gold (₹/10 g); silver (₹/kg); 10-year G-sec yield (%)
  "movers": { "gainers": [ { "name": "Company", "pct": 0 } ], "losers": [], "source": "" },   // Nifty 50, five each
  "sectors": [ { "name": "Bank", "name_hi": "बैंक", "pct": 0 } ],                              // Nifty sector indices, % change
  "flows": { "date": "2026-10-30", "fii": 0, "dii": 0, "unit": "₹ crore", "source": "" },      // NSE provisional cash-market net
  "notes": []
}
```

During market hours the hourly run updates `value`, `change`, `pct`, movers, sectors and rates, with `status: "open"`. After the close it writes the final values, appends the close to each index `history` (dropping anything beyond 30 sessions), and adds the day's FII/DII flows once NSE publishes them (usually by 7 pm IST). `change` and `pct` are against the previous session's close. Up and down colours come from the sign, so a fall must be a negative number.
