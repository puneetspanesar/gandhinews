// Prints how many queries found candidates; fails when none did (a broken search, not a lack of photos).
import fs from 'node:fs';
const c = JSON.parse(fs.readFileSync('photo-candidates/candidates.json', 'utf8'));
const keys = Object.keys(c);
const empty = keys.filter((k) => !(c[k].candidates || []).length);
console.log(`${keys.length} queries, ${empty.length} with no candidates${empty.length ? ': ' + empty.join(' ') : ''}`);
if (keys.length && empty.length === keys.length) { console.log('::error::every query came back empty'); process.exit(1); }
