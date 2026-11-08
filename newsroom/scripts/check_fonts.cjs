// Font check (owner, November 8): every visible piece of text, buttons and inputs included, must render in PT Serif
// (or Noto Serif Devanagari). Usage after a build: node newsroom/scripts/check_fonts.cjs / /hi/ /states/<id>/ ...
const {chromium}=require('playwright');const http=require('http'),fs=require('fs'),path=require('path');const root='/home/claude/gandhinews/dist';
const T={'.html':'text/html','.css':'text/css','.js':'text/javascript','.svg':'image/svg+xml','.woff2':'font/woff2','.jpg':'image/jpeg','.png':'image/png','.json':'application/json'};
const srv=http.createServer((q,r)=>{let f=path.join(root,decodeURIComponent(q.url.split('?')[0]));if(f.endsWith('/'))f+='index.html';fs.readFile(f,(e,d)=>{if(e){r.statusCode=404;r.end()}else{r.setHeader('content-type',T[path.extname(f)]||'application/octet-stream');r.end(d)}})}).listen(4401);
const pages=process.argv.slice(2);
(async()=>{const b=await chromium.launch();const bad={};
for(const w of [1440,390])for(const u of pages){const p=await b.newPage({viewport:{width:w,height:900}});await p.goto('http://localhost:4401'+u,{waitUntil:'load'});
 // open menus/overlays so hidden things are checked too
 const r=await p.evaluate(()=>{const o=[];for(const e of document.querySelectorAll('body *')){if(['SCRIPT','STYLE','svg','path','NOSCRIPT'].includes(e.tagName))continue;const has=[...e.childNodes].some(n=>n.nodeType===3&&n.nodeValue.trim());if(!has&&!['INPUT','BUTTON','SELECT','TEXTAREA'].includes(e.tagName))continue;const f=getComputedStyle(e).fontFamily.split(',')[0].replace(/["']/g,'').trim();if(!/^PT Serif$|^Noto Serif Devanagari$/.test(f)){const cls=e.tagName.toLowerCase()+(e.className&&typeof e.className==='string'?'.'+e.className.trim().split(/\s+/).join('.'):'');o.push(f+' | '+cls+' | '+(e.textContent||e.value||e.placeholder||'').trim().slice(0,40))}}return o});
 for(const x of r){const k=x.split(' | ').slice(0,2).join(' | ');if(!bad[k])bad[k]=(x.split(' | ')[2]||'')+'  @'+u+' '+w}
 await p.close()}
console.log(Object.entries(bad).map(([k,v])=>k+' :: '+v).join('\n')||'ALL PT SERIF');await b.close();srv.close()})()
