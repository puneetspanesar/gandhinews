// Gandhi News API Worker. Pages are static assets; only /api/* runs here (see wrangler.jsonc).
// Morning Brief subscriptions: signup -> confirmation email -> confirmed; one-click unsubscribe.
// Subscribers live in our own D1 database (binding DB). Email is delivered through Amazon SES.
import { AwsClient } from 'aws4fetch';

interface Env {
  ASSETS?: { fetch: (r: Request) => Promise<Response> };
  DB?: D1Database;
  EMAIL?: { send: (m: any) => Promise<any> }; // Cloudflare Email Service binding (confirmation emails)
  MAIL_FROM_ADDRESS?: string; // e.g. brief@lokvox.com
  AWS_ACCESS_KEY_ID?: string;
  AWS_SECRET_ACCESS_KEY?: string;
  AWS_REGION?: string; // e.g. ap-south-1
  MAIL_FROM?: string; // e.g. "Gandhi News <brief@lokvox.com>"
  ADMIN_TOKEN?: string;
  SITE_URL?: string;
}
type Lang = 'en' | 'hi';

const SITE = (env: Env) => (env.SITE_URL || 'https://gandhinews.com').replace(/\/$/, '');
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
    subject: 'Confirm your Gandhi News Morning Brief',
    pre: 'One click and you are in. Here is what lands in your inbox every weekday.',
    kicker: 'The Morning Brief',
    h: 'One click and you are in',
    p: 'Confirm your email and the Gandhi News Morning Brief will start arriving every weekday morning.',
    btn: 'Confirm my email',
    what: 'What you will get',
    items: [['newspaper', 'Five stories that matter', 'Politics, policy, the economy and Parliament, in short.'], ['chart-line', 'One chart a day', 'The number behind the news, drawn clearly.'], ['translate', 'In your language', 'English or हिंदी, whichever you chose.']],
    latest: 'On Gandhi News today',
    read: 'Read on gandhinews.com',
    ignore: 'You are receiving this because someone signed up for the Morning Brief with this address at gandhinews.com. If it was not you, ignore this email and you will not hear from us again.',
    tag: 'The people’s newsroom',
  },
  hi: {
    subject: 'गांधी न्यूज़ मॉर्निंग ब्रीफ की पुष्टि करें',
    pre: 'बस एक क्लिक बाकी है। हर कामकाजी दिन आपके इनबॉक्स में क्या आएगा, यहां देखें।',
    kicker: 'मॉर्निंग ब्रीफ',
    h: 'बस एक क्लिक बाकी है',
    p: 'अपने ईमेल की पुष्टि करें, और गांधी न्यूज़ मॉर्निंग ब्रीफ हर कामकाजी दिन की सुबह आपके पास पहुंचने लगेगा।',
    btn: 'मेरा ईमेल पुष्ट करें',
    what: 'आपको क्या मिलेगा',
    items: [['newspaper', 'पांच ज़रूरी खबरें', 'राजनीति, नीति, अर्थव्यवस्था और संसद, संक्षेप में।'], ['chart-line', 'रोज़ एक चार्ट', 'खबर के पीछे का आंकड़ा, साफ-साफ।'], ['translate', 'आपकी भाषा में', 'हिंदी या English, जो आपने चुनी।']],
    latest: 'आज गांधी न्यूज़ पर',
    read: 'gandhinews.com पर पढ़ें',
    ignore: 'यह ईमेल आपको इसलिए मिला है क्योंकि gandhinews.com पर इस पते से मॉर्निंग ब्रीफ के लिए साइन अप किया गया। अगर यह आपने नहीं किया, तो इसे अनदेखा करें। आपको हमसे आगे कोई ईमेल नहीं मिलेगा।',
    tag: 'जनता का न्यूज़रूम',
  },
};
const escHtml = (x: string) => x.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

/** Latest three stories from the site's RSS feed, for the "On Gandhi News today" block. */
async function latestStories(env: Env, lang: Lang): Promise<{ title: string; link: string }[]> {
  try {
    const url = `${SITE(env)}${pfx(lang)}/rss.xml`;
    const r = env.ASSETS ? await env.ASSETS.fetch(new Request(url)) : await fetch(url);
    const xml = await r.text();
    const items = [...xml.matchAll(/<item>[\s\S]*?<title>([\s\S]*?)<\/title>[\s\S]*?<link>([\s\S]*?)<\/link>/g)].slice(0, 3);
    const un = (x: string) => x.replace(/<!\[CDATA\[|\]\]>/g, '').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'").trim();
    return items.map((m) => ({ title: un(m[1]), link: un(m[2]) }));
  } catch { return []; }
}

function confirmEmail(lang: Lang, link: string, site: string, stories: { title: string; link: string }[]) {
  const c = COPY[lang];
  const f = lang === 'hi' ? "'Noto Sans Devanagari','Mangal',Arial,sans-serif" : "Inter,'Helvetica Neue',Arial,sans-serif";
  const h = "'Google Sans','Helvetica Neue',Arial,sans-serif";
  const img = (n: string) => `${site}/email/${n}.png`;
  const items = c.items.map(([ic, t, d]) => `<tr><td width="40" valign="top" style="padding:14px 0 14px 0"><img src="${img(ic)}" width="28" height="28" alt="" style="display:block;border:0"></td><td valign="top" style="padding:14px 0;border-bottom:1px solid #eeeeee"><div style="font:600 16px/1.4 ${f};color:#0d0d0d">${t}</div><div style="font:15px/1.5 ${f};color:#555555;margin-top:2px">${d}</div></td></tr>`).join('');
  const news = stories.length ? `<tr><td style="padding:8px 36px 28px"><div style="font:600 13px/1 ${h};color:#cc0000;letter-spacing:.02em;margin:0 0 6px">${c.latest}</div>${stories.map((s, i) => `<a href="${escHtml(s.link)}" style="display:block;text-decoration:none;padding:14px 0;border-top:${i ? '1px solid #eeeeee' : '2px solid #0d0d0d'}"><span style="font:600 17px/1.4 ${f};color:#0d0d0d">${escHtml(s.title)}</span></a>`).join('')}<a href="${site}${lang === 'hi' ? '/hi/' : '/'}" style="display:inline-block;margin-top:6px;font:600 14px ${h};color:#cc0000;text-decoration:none">${c.read} &rarr;</a></td></tr>` : '';
  const html = `<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>${c.subject}</title></head>
<body style="margin:0;padding:0;background:#f2f2f2">
<div style="display:none;max-height:0;overflow:hidden;opacity:0">${c.pre}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f2f2f2"><tr><td align="center" style="padding:28px 12px">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border:1px solid #e4e4e4;border-radius:8px">
<tr><td style="padding:22px 36px;border-bottom:1px solid #eeeeee"><table role="presentation" cellpadding="0" cellspacing="0"><tr><td><img src="${img('seal')}" width="36" height="36" alt="Gandhi News" style="display:block;border:0"></td><td style="padding-left:10px;font:700 21px ${h};color:#0d0d0d">Gandhi News</td></tr></table></td></tr>
<tr><td style="padding:34px 36px 8px">
<div style="font:600 13px/1 ${h};color:#cc0000;letter-spacing:.02em">${c.kicker}</div>
<h1 style="margin:10px 0 12px;font:700 28px/1.25 ${lang === 'hi' ? f : h};color:#0d0d0d">${c.h}</h1>
<p style="margin:0 0 24px;font:16px/1.6 ${f};color:#333333">${c.p}</p>
<table role="presentation" cellpadding="0" cellspacing="0"><tr><td style="border-radius:24px;background:#cc0000"><a href="${link}" style="display:inline-block;padding:14px 28px;font:600 16px ${h};color:#ffffff;text-decoration:none;border-radius:24px">${c.btn}</a></td></tr></table>
</td></tr>
<tr><td style="padding:30px 36px 18px"><div style="font:600 13px/1 ${h};color:#cc0000;letter-spacing:.02em;margin:0 0 4px">${c.what}</div><table role="presentation" width="100%" cellpadding="0" cellspacing="0">${items}</table></td></tr>
${news}
<tr><td style="background:#0d0d0d;padding:24px 36px;border-radius:0 0 8px 8px">
<div style="font:600 15px ${h};color:#ffffff">Gandhi News <span style="color:#9a9a9a;font-weight:400">· ${c.tag}</span></div>
<p style="margin:10px 0 0;font:12px/1.6 ${f};color:#9a9a9a">${c.ignore}</p>
</td></tr>
</table>
<p style="margin:16px 0 0;font:12px ${f};color:#999999"><a href="${site}" style="color:#999999">gandhinews.com</a></p>
</td></tr></table></body></html>`;
  const text = `${c.h}\n\n${c.p}\n\n${c.btn}: ${link}\n\n${c.what}:\n${c.items.map(([, t, d]) => `- ${t}: ${d}`).join('\n')}\n\n${stories.length ? `${c.latest}:\n${stories.map((s) => `- ${s.title}\n  ${s.link}`).join('\n')}\n\n` : ''}${c.ignore}\n\nGandhi News · ${c.tag}`;
  return { subject: c.subject, html, text };
}

// Delivery: Cloudflare Email Service when bound (used for confirmation emails now); Amazon SES otherwise (planned for the daily brief).
async function sendEmail(env: Env, to: string, msg: { subject: string; html: string; text: string }, unsubUrl?: string) {
  if (env.EMAIL && !unsubUrl) {
    const from = env.MAIL_FROM_ADDRESS || 'brief@lokvox.com';
    try {
      const r = await env.EMAIL.send({ to, from: { email: from, name: 'Gandhi News' }, subject: msg.subject, html: msg.html, text: msg.text });
      return { ok: true, info: `cf:${r?.messageId ?? 'sent'}` };
    } catch (e1: any) {
      try {
        const r = await env.EMAIL.send({ to, from, subject: msg.subject, html: msg.html, text: msg.text });
        return { ok: true, info: `cf:${r?.messageId ?? 'sent'}` };
      } catch (e2: any) {
        return { ok: false, info: `cf-error: ${String(e2?.message || e2).slice(0, 300)}` };
      }
    }
  }
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
  const res = await sendEmail(env, email, confirmEmail(lang, link, SITE(env), await latestStories(env, lang)));
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
      if (url.pathname === '/api/health') return json({ ok: true, db: Boolean(env.DB), email: Boolean(env.EMAIL), ses: Boolean(env.AWS_ACCESS_KEY_ID && env.MAIL_FROM) });
      return json({ error: 'not found' }, 404);
    } catch (e: any) {
      console.error(e);
      return json({ error: 'server error' }, 500);
    }
  },
};
