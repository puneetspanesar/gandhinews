"""English content: day-month dates -> month day, year (owner rule). Usage: dates.py <files...> [--dry]"""
import re, sys
M = 'January|February|March|April|May|June|July|August|September|October|November|December'
A = 'Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec'
MON = rf'(?:{M}|(?:{A})\.?)'
WD = r'(?:(?P<wd>Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+)?'
# ranges first: "3-5 November 2026", "3 to 5 November", "5 and 6 November"
RANGE = re.compile(rf'\b(?P<d1>\d{{1,2}})(?P<sep>\s*[-–]\s*|\s+to\s+|\s+and\s+)(?P<d2>\d{{1,2}})\s+(?P<m>{MON})(?:,?\s+(?P<y>(?:19|20)\d\d))?\b')
# cross-month range: "28 October to 2 November 2026" handled as two singles.
SINGLE = re.compile(rf'\b{WD}(?P<d>\d{{1,2}})(?:st|nd|rd|th)?\s+(?:of\s+)?(?P<m>{MON})(?:,?\s+(?P<y>(?:19|20)\d\d))?(?P<after>\b)')
def fix_line(s):
    def rr(m):
        y = f", {m['y']}" if m['y'] else ''
        sep = m['sep'] if m['sep'].strip() in ('to', 'and') else '-'
        if m['sep'].strip() in ('to', 'and'): sep = f" {m['sep'].strip()} "
        return f"{m['m']} {m['d1']}{sep}{m['d2']}{y}"
    s = RANGE.sub(rr, s)
    def rs(m):
        wd = f"{m['wd']}, " if m['wd'] else ''
        y = f", {m['y']}" if m['y'] else ''
        return f"{wd}{m['m']} {int(m['d'])}{y}"
    out = SINGLE.sub(rs, s)
    # comma after a year that sits mid-sentence: "on November 5, 2026 the court" -> "..., 2026, the court"
    out = re.sub(rf'((?:{M}|{A})\.? \d{{1,2}}, (?:19|20)\d\d) (?=[a-z])', r'\1, ', out)
    return out
dry = '--dry' in sys.argv
n_files = n_changes = 0
for p in [a for a in sys.argv[1:] if not a.startswith('--')]:
    lines = open(p, encoding='utf-8').read().split('\n')
    in_src = False; changed = 0
    for i, l in enumerate(lines):
        if re.match(r'^sources:\s*$', l): in_src = True; continue
        if in_src and (l.startswith('  ') or l.startswith('- ') or not l.strip()):
            if not l.strip() or l.startswith('  ') or l.startswith('- '): 
                if re.match(r'^\S', l) and not l.startswith('- '): in_src = False
                else: continue
        elif in_src: in_src = False
        if 'http' in l and re.search(r'https?://\S*\d{1,2}[-_ ](?:' + M + ')', l): continue
        nl = fix_line(l)
        if nl != l:
            changed += 1
            if dry and changed <= 3: print(f'{p}:{i+1}\n  - {l.strip()[:150]}\n  + {nl.strip()[:150]}')
            lines[i] = nl
    if changed:
        n_files += 1; n_changes += changed
        if not dry: open(p, 'w', encoding='utf-8').write('\n'.join(lines))
print(f'{n_files} files, {n_changes} lines changed' + (' (dry run)' if dry else ''))
