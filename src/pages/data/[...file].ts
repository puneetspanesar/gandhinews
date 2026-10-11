// Serves the tracker data files at /data/*.json and /data/hi/*.json (source: /content/data).
import fs from 'node:fs';
import path from 'node:path';
import { CONTENT } from '../../lib/routes.mjs';
export function getStaticPaths() {
  const dir = path.join(CONTENT, 'data');
  const files = [
    ...fs.readdirSync(dir).filter((f) => f.endsWith('.json')),
    ...fs.readdirSync(path.join(dir, 'hi')).filter((f) => f.endsWith('.json')).map((f) => `hi/${f}`),
  ];
  return files.map((file) => ({ params: { file } }));
}
export function GET({ params }: { params: { file: string } }) {
  const body = fs.readFileSync(path.join(CONTENT, 'data', params.file), 'utf8');
  return new Response(body, { headers: { 'Content-Type': 'application/json; charset=utf-8' } });
}
