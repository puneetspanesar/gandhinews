// LokVox API Worker. Pages are static assets; only /api/* runs here (see wrangler.jsonc).
// Morning Brief subscriptions: signup -> confirmation email -> confirmed; one-click unsubscribe.
// Subscribers live in our own D1 database (binding DB). Email is delivered through Amazon SES.
import { AwsClient } from 'aws4fetch';

interface Env {
  DB?: D1Database;
  AWS_ACCESS_KEY_ID?: string;
  AWS_SECRET_ACCESS_KEY?: string;
  AWS_REGION?: string; // e.g. ap-south-1
  MAIL_FROM?: string; // e.g. "LokVox <brief@lokvox.com>"
  ADMIN_TOKEN?: string;
  SITE_URL?: string;
}
type Lang = 'en' | 'hi';

const SITE = (env: Env) => (env.SITE_URL || 'https://lokvox.com').replace(/\/$/, '');
const pfx = (lang: Lang) => (lang === 'hi' ? '/hi' : '');
const json = (data: unknown, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });
const redirect = (url: string) => new Response(null, { status: 303, headers: { location: url, 'cache-control': 'no-store' } });
const EMAIL_RE = /^[^\s@<>()[\],;:"]+@[^\s@<>()[\],;:"]+\.[a-z]{2,}$/i;

function token() {
  const b = new Uint8Array(24);
  crypto.getRandomValues(b);
  return btoa(String.fromCharCode(...b)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}
async function sha256(s: string) {
  const d = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
  return [...new Uint8Array(d)].map((x) => x.toString(16).padStart(2, '0')).join('');
}

let schemaReady = false;
async function ensureSchema(db: D1Database) {
  if (schemaReady) return;
  await db.batch([
    db.prepare(`CREATE TABLE IF NOT EXISTS subscribers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT NOT NULL UNIQUE,
      lang TEXT NOT NULL DEFAULT 'en',
      status TEXT NOT NULL DEFAULT 'pending',
      confirm_token TEXT,
      unsub_token TEXT NOT NULL,
      created_at TEXT NOT NULL,
      confirmed_at TEXT,
      unsubscribed_at TEXT,
      consent_ip_hash TEXT,
      consent_ua TEXT,
      source TEXT
    )`),
    db.prepare(`CREATE INDEX IF NOT EXISTS idx_sub_status ON subscribers(status, lang)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS sends (id INTEGER PRIMARY KEY AUTOINCREMENT, subscriber_id INTEGER, kind TEXT, sent_at TEXT, ok INTEGER, info TEXT)`),
  ]);
  schemaReady = true;
}

// ---------- email ----------
const COPY = {
  en: {
    subject: 'Confirm your LokVox Morning Brief',
    pre: 'One click and you are in.',
    h: 'Confirm your subscription',
    p: 'Thanks for signing up for the LokVox Morning Brief: the stories that matter, with one chart, every weekday morning.',
    btn: 'Confirm my email',
    ignore: 'If you did not sign up, ignore this email and you will not hear from us again.',
    foot: 'LokVox, the people’s newsroom',
  },
  hi: {
    subject: 'लोकवॉक्स मॉर्निंग ब्रीफ की पुष्टि करें',
    pre: 'बस एक क्लिक बाकी है।',
    h: 'अपनी सदस्यता की पुष्टि करें',
    p: 'लोकवॉक्स मॉर्निंग ब्रीफ के लिए साइन अप करने का शुक्रिया: ज़रूरी खबरें, एक चार्ट के साथ, हर कार्यदिवस की सुबह।',
    btn: 'मेरा ईमेल पुष्ट करें',
    ignore: 'अगर आपने साइन अप नहीं किया, तो इस ईमेल को अनदेखा करें। आपको हमसे आगे कोई ईमेल नहीं मिलेगा।',
    foot: 'लोकवॉक्स, जनता का न्यूज़रूम',
  },
};

function confirmEmail(lang: Lang, link: string) {
  const c = COPY[lang];
  const font = lang === 'hi' ? "'Noto Sans Devanagari',Arial,sans-serif" : 'Inter,Arial,sans-serif';
  const html = `<!doctype html><html lang="${lang}"><body style="margin:0;background:#f4f4f4">
<span style="display:none;max-height:0;overflow:hidden">${c.pre}</span>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4"><tr><td align="center" style="padding:32px 16px">
<table role="presentation" width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;background:#ffffff;border:1px solid #e3e3e3;border-radius:6px">
<tr><td style="background:#0d0d0d;padding:18px 28px;border-radius:6px 6px 0 0"><span style="display:inline-block;width:30px;height:30px;border-radius:15px;background:#cc0000;color:#fff;text-align:center;line-height:30px;font:700 17px ${font};vertical-align:middle">ल</span><span style="font:600 20px Arial,sans-serif;color:#fff;vertical-align:middle;margin-left:10px">LokVox</span></td></tr>
<tr><td style="padding:28px;font-family:${font};color:#0d0d0d">
<h1 style="margin:0 0 12px;font-size:22px;line-height:1.3">${c.h}</h1>
<p style="margin:0 0 22px;font-size:16px;line-height:1.6;color:#333">${c.p}</p>
<a href="${link}" style="display:inline-block;background:#cc0000;color:#ffffff;text-decoration:none;font-weight:600;font-size:16px;padding:12px 22px;border-radius:22px">${c.btn}</a>
<p style="margin:22px 0 0;font-size:13px;line-height:1.6;color:#777">${c.ignore}</p>
</td></tr>
<tr><td style="padding:16px 28px;border-top:1px solid #eee;font:13px ${font};color:#999">${c.foot} · lokvox.com</td></tr>
</table></td></tr></table></body></html>`;
  const text = `${c.h}\n\n${c.p}\n\n${c.btn}: ${link}\n\n${c.ignore}\n\n${c.foot}`;
  return { subject: c.subject, html, text };
}

async function sendEmail(env: Env, to: string, msg: { subject: string; html: string; text: string }, unsubUrl?: string) {
  if (!env.AWS_ACCESS_KEY_ID || !env.AWS_SECRET_ACCESS_KEY || !env.MAIL_FROM) return { ok: false, info: 'ses-not-configured' };
  const region = env.AWS_REGION || 'ap-south-1';
  const aws = new AwsClient({ accessKeyId: env.AWS_ACCESS_KEY_ID, secretAccessKey: env.AWS_SECRET_ACCESS_KEY, service: 'ses', region });
  const body: any = {
    FromEmailAddress: env.MAIL_FROM,
    Destination: { ToAddresses: [to] },
    Content: { Simple: { Subject: { Data: msg.subject, Charset: 'UTF-8' }, Body: { Html: { Data: msg.html, Charset: 'UTF-8' }, Text: { Data: msg.text, Charset: 'UTF-8' } } } },
  };
  if (unsubUrl) {
    body.Content.Simple.Headers = [
      { Name: 'List-Unsubscribe', Value: `<${unsubUrl}>` },
      { Name: 'List-Unsubscribe-Post', Value: 'List-Unsubscribe=One-Click' },
    ];
  }
  const r = await aws.fetch(`https://email.${region}.amazonaws.com/v2/email/outbound-emails`, {
    method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body),
  });
  return { ok: r.ok, info: r.ok ? 'sent' : `ses-${r.status}: ${(await r.text()).slice(0, 300)}` };
}

// ---------- handlers ----------
async function subscribe(req: Request, env: Env) {
  const ct = req.headers.get('content-type') || '';
  const wantsJson = ct.includes('application/json') || (req.headers.get('accept') || '').includes('application/json');
  let email = '', lang: Lang = 'en', source = '', trap = '';
  if (ct.includes('application/json')) {
    const b: any = await req.json().catch(() => ({}));
    email = String(b.email || ''); lang = b.lang === 'hi' ? 'hi' : 'en'; source = String(b.source || ''); trap = String(b.website || '');
  } else {
    const f = await req.formData();
    email = String(f.get('email') || ''); lang = f.get('lang') === 'hi' ? 'hi' : 'en'; source = String(f.get('source') || ''); trap = String(f.get('website') || '');
  }
  email = email.trim().toLowerCase();
  const done = (status: string) => (wantsJson ? json({ ok: status !== 'invalid', status }, status === 'invalid' ? 400 : 200) : redirect(`${SITE(env)}${pfx(lang)}/subscribe/${status === 'invalid' ? '?error=email' : 'check-email/'}`));
  if (trap) return done('pending'); // honeypot: pretend success
  if (!EMAIL_RE.test(email) || email.length > 200) return done('invalid');
  if (!env.DB) return wantsJson ? json({ ok: false, status: 'unavailable' }, 503) : redirect(`${SITE(env)}${pfx(lang)}/subscribe/?error=later`);
  await ensureSchema(env.DB);

  const now = new Date().toISOString();
  const ipHash = await sha256((req.headers.get('cf-connecting-ip') || '') + 'lokvox');
  const ua = (req.headers.get('user-agent') || '').slice(0, 200);
  const existing: any = await env.DB.prepare('SELECT * FROM subscribers WHERE email = ?').bind(email).first();
  if (existing && existing.status === 'confirmed') {
    if (existing.lang !== lang) await env.DB.prepare('UPDATE subscribers SET lang = ? WHERE id = ?').bind(lang, existing.id).run();
    return done('confirmed');
  }
  const ctoken = token();
  if (existing) {
    // Limit repeat confirmation emails to one every 10 minutes.
    if (existing.status === 'pending' && existing.created_at > new Date(Date.now() - 10 * 60 * 1000).toISOString()) return done('pending');
    await env.DB.prepare(`UPDATE subscribers SET lang=?, status='pending', confirm_token=?, created_at=?, unsubscribed_at=NULL, consent_ip_hash=?, consent_ua=?, source=? WHERE id=?`)
      .bind(lang, ctoken, now, ipHash, ua, source, existing.id).run();
  } else {
    await env.DB.prepare(`INSERT INTO subscribers (email, lang, status, confirm_token, unsub_token, created_at, consent_ip_hash, consent_ua, source) VALUES (?, ?, 'pending', ?, ?, ?, ?, ?, ?)`)
      .bind(email, lang, ctoken, token(), now, ipHash, ua, source).run();
  }
  const link = `${SITE(env)}/api/confirm?t=${encodeURIComponent(ctoken)}`;
  const res = await sendEmail(env, email, confirmEmail(lang, link));
  const row: any = await env.DB.prepare('SELECT id FROM subscribers WHERE email = ?').bind(email).first();
  await env.DB.prepare('INSERT INTO sends (subscriber_id, kind, sent_at, ok, info) VALUES (?, ?, ?, ?, ?)').bind(row?.id ?? null, 'confirm', now, res.ok ? 1 : 0, res.info).run();
  return done('pending');
}

async function confirm(url: URL, env: Env) {
  const t = url.searchParams.get('t') || '';
  if (!env.DB || !t) return redirect(`${SITE(env)}/subscribe/?error=link`);
  await ensureSchema(env.DB);
  const row: any = await env.DB.prepare('SELECT * FROM subscribers WHERE confirm_token = ?').bind(t).first();
  if (!row) return redirect(`${SITE(env)}/subscribe/?error=link`);
  await env.DB.prepare(`UPDATE subscribers SET status='confirmed', confirmed_at=?, confirm_token=NULL WHERE id=?`).bind(new Date().toISOString(), row.id).run();
  return redirect(`${SITE(env)}${pfx(row.lang)}/subscribe/confirmed/`);
}

async function unsubscribe(req: Request, url: URL, env: Env) {
  const t = url.searchParams.get('t') || '';
  if (!env.DB || !t) return redirect(`${SITE(env)}/subscribe/?error=link`);
  await ensureSchema(env.DB);
  const row: any = await env.DB.prepare('SELECT * FROM subscribers WHERE unsub_token = ?').bind(t).first();
  if (row) await env.DB.prepare(`UPDATE subscribers SET status='unsubscribed', unsubscribed_at=? WHERE id=?`).bind(new Date().toISOString(), row.id).run();
  if (req.method === 'POST') return new Response('Unsubscribed', { status: 200 }); // one-click (RFC 8058)
  return redirect(`${SITE(env)}${pfx(row?.lang === 'hi' ? 'hi' : 'en')}/subscribe/unsubscribed/`);
}

async function stats(req: Request, env: Env) {
  if (!env.ADMIN_TOKEN || req.headers.get('authorization') !== `Bearer ${env.ADMIN_TOKEN}`) return json({ error: 'unauthorized' }, 401);
  if (!env.DB) return json({ error: 'no database' }, 503);
  await ensureSchema(env.DB);
  const r = await env.DB.prepare('SELECT status, lang, COUNT(*) AS n FROM subscribers GROUP BY status, lang').all();
  return json({ ses: Boolean(env.AWS_ACCESS_KEY_ID && env.MAIL_FROM), rows: r.results });
}

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url);
    try {
      if (url.pathname === '/api/subscribe' && req.method === 'POST') return await subscribe(req, env);
      if (url.pathname === '/api/confirm' && req.method === 'GET') return await confirm(url, env);
      if (url.pathname === '/api/unsubscribe') return await unsubscribe(req, url, env);
      if (url.pathname === '/api/admin/stats') return await stats(req, env);
      if (url.pathname === '/api/health') return json({ ok: true, db: Boolean(env.DB), ses: Boolean(env.AWS_ACCESS_KEY_ID && env.MAIL_FROM) });
      return json({ error: 'not found' }, 404);
    } catch (e: any) {
      console.error(e);
      return json({ error: 'server error' }, 500);
    }
  },
};
