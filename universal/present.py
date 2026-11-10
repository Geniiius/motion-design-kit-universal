"""Standalone HTML service decks and progressive infographics. No third-party JS, no network.

One file, two lives: in a browser it is a real interactive deck; under the Prompt Motion
renderer (window.__RENDERING__) it plays as a deterministic film driven by seek(t).
All user-supplied content is HTML-escaped. A price or benefit is shown only if supplied.
"""
from __future__ import annotations
import html
import json
import re
from pathlib import Path

TEXT = {
    'fr': dict(lang='fr', menu='Choisissez un service', tag='Service', back='← Tous les services', benefits='Bénéfices', price='Tarif', ask='Tarif sur devis, non indiqué ici', more='En savoir plus',
               prev='Précédent', next='Suivant', compare='Comparer avant et après', before='Avant', after='Après', steps='Comment ça marche', step='Étape suivante', restart='Recommencer', points='Explorer le schéma',
               foot='Navigation au clic, au clavier (flèches, Échap) et au toucher', chapters='Chapitres', infotag='Infographie pédagogique', source='Source / hypothèse', stepl='Étape'),
    'es': dict(lang='es', menu='Elige un servicio', tag='Servicio', back='← Todos los servicios', benefits='Beneficios', price='Precio', ask='Precio a consultar, no indicado aquí', more='Saber más',
               prev='Anterior', next='Siguiente', compare='Comparar antes y después', before='Antes', after='Después', steps='Cómo funciona', step='Paso siguiente', restart='Reiniciar', points='Explorar el esquema',
               foot='Navegación con clic, teclado (flechas, Esc) y táctil', chapters='Capítulos', infotag='Infografía pedagógica', source='Fuente / hipótesis', stepl='Paso'),
    'en': dict(lang='en', menu='Choose a service', tag='Service', back='← All services', benefits='Benefits', price='Price', ask='Price on request, not listed here', more='Learn more',
               prev='Previous', next='Next', compare='Compare before and after', before='Before', after='After', steps='How it works', step='Next step', restart='Start over', points='Explore the diagram',
               foot='Works with click, keyboard (arrows, Esc) and touch', chapters='Chapters', infotag='Educational infographic', source='Source / assumption', stepl='Step'),
}


def esc(x):
    return html.escape(str(x), quote=True)


def color(x: str) -> str:
    return x if isinstance(x, str) and re.fullmatch(r'#[0-9a-fA-F]{6}', x) else '#7c6cff'


CSS = '''
:root{font-family:"Segoe UI",system-ui,-apple-system,Roboto,sans-serif;--accent:ACCENT;--ink:#f3f4f8;--muted:#b4bdd0;--line:#333c55;--panel:#171d2e;--panel2:#1f2740;color:var(--ink);background:#0b0f1c;color-scheme:dark}
*{box-sizing:border-box}html,body{margin:0;min-height:100%}body{min-height:100vh;display:flex;flex-direction:column;background:radial-gradient(ellipse at 85% 5%,color-mix(in srgb,var(--accent) 30%,#0b0f1c) 0%,#0f1426 40%,#0b0f1c 100%);line-height:1.5;overflow-x:hidden}
header,main,footer{width:100%;max-width:1180px;margin-inline:auto;padding-inline:clamp(16px,4vw,48px)}
header{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:12px;padding-block:20px}.brand{font-weight:800;letter-spacing:.04em}
main{flex:1;padding-block:8px 32px}footer{color:#a3adc2;padding-block:16px 28px;font-size:.82rem}
h1{font-size:clamp(2.1rem,6vw,4.4rem);line-height:1.05;letter-spacing:-.02em;margin:.4em 0 .3em;text-wrap:balance}h2{font-size:clamp(1.35rem,2.8vw,1.9rem);line-height:1.2;margin:.2em 0 .4em}h3{font-size:1.05rem;margin:1.6em 0 .5em}
p{color:var(--muted);max-width:66ch;margin:.4em 0}.eyebrow,.tag{color:color-mix(in srgb,var(--accent) 55%,white);font-weight:600;font-size:1rem;margin:0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,290px),1fr));gap:16px;margin:28px 0}
.tile{position:relative;display:flex;flex-direction:column;align-items:flex-start;gap:6px;background:linear-gradient(150deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:18px;padding:22px;transition:transform .22s cubic-bezier(.2,.8,.2,1),border-color .22s}
.tile:hover,.tile:focus-within{transform:translateY(-4px);border-color:var(--accent)}.tile button{margin-top:auto}
button,.cta{font:inherit;font-weight:600;cursor:pointer;border:1px solid #6b78a3;background:#242d49;color:#fff;padding:10px 16px;border-radius:12px;min-height:44px;min-width:44px;transition:background .15s,border-color .15s,transform .1s;text-decoration:none;display:inline-flex;align-items:center;justify-content:center}
button:hover,.cta:hover{border-color:var(--accent);background:#2d3858}button:active{transform:scale(.97)}:focus-visible{outline:3px solid color-mix(in srgb,var(--accent) 60%,white);outline-offset:2px}
.primary,.cta{background:color-mix(in srgb,var(--accent) 78%,black);border-color:transparent}.primary:hover,.cta:hover{background:color-mix(in srgb,var(--accent) 88%,black)}
.chapters{display:flex;flex-wrap:wrap;gap:8px;margin:0;padding:0;list-style:none}.chapters button{padding:6px 12px;min-height:44px;font-size:.86rem;background:transparent;border-color:var(--line);color:var(--muted)}.chapters button[aria-current="true"]{background:var(--accent);border-color:transparent;color:#fff}
.detail{background:linear-gradient(150deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:22px;padding:clamp(18px,4vw,40px);margin-top:12px;animation:arrive .36s cubic-bezier(.2,.8,.2,1)}.detail:focus{outline:none}
.detail h2{font-size:clamp(1.8rem,4vw,3rem);letter-spacing:-.01em}.row{display:flex;flex-wrap:wrap;gap:10px;justify-content:space-between;margin-top:24px}
ul.benefits{display:grid;gap:8px;padding:0;margin:0;list-style:none}ul.benefits li{padding-left:26px;position:relative;color:var(--ink)}ul.benefits li::before{content:"";position:absolute;left:4px;top:.55em;width:10px;height:10px;border-radius:50%;background:var(--accent)}
.compare{position:relative;border-radius:16px;overflow:hidden;border:1px solid var(--line);margin:8px 0;aspect-ratio:16/5;min-height:150px;--pos:50%;touch-action:pan-y}
.compare .side{position:absolute;inset:0;display:flex;align-items:center;padding:clamp(12px,3vw,28px);font-weight:600}.compare .side b{display:block;font-size:.72rem;text-transform:uppercase;letter-spacing:.14em;opacity:.8}.compare .a{background:#222838;color:#d8dcea}.compare .b{background:color-mix(in srgb,var(--accent) 62%,#111);color:#fff;justify-content:flex-end;text-align:right;clip-path:inset(0 0 0 var(--pos))}
.compare .bar{position:absolute;top:0;bottom:0;left:var(--pos);width:3px;background:#fff;transform:translateX(-1.5px);pointer-events:none}.compare input{position:absolute;inset:0;width:100%;height:100%;margin:0;opacity:0;cursor:ew-resize}
.compare:focus-within{outline:3px solid color-mix(in srgb,var(--accent) 60%,white);outline-offset:2px}
.steps{display:grid;gap:10px;grid-template-columns:repeat(auto-fit,minmax(min(100%,200px),1fr));margin:8px 0;padding:0;list-style:none}.steps li{background:#111728;border:1px solid var(--line);border-radius:14px;padding:14px;opacity:.28;transform:translateY(8px);transition:opacity .3s,transform .3s cubic-bezier(.2,.8,.2,1)}.steps li.on{opacity:1;transform:none;border-color:var(--accent)}.steps strong{display:block;color:#fff}
.map{position:relative;aspect-ratio:16/5;min-height:170px;border-radius:16px;border:1px solid var(--line);background:linear-gradient(120deg,#151b2d,#1d2540);margin:8px 0}.pin{position:absolute;transform:translate(-50%,-50%);border-radius:50%;width:44px;height:44px;padding:0;background:var(--accent);border:3px solid #fff}.pin[aria-pressed="true"]{box-shadow:0 0 0 6px color-mix(in srgb,var(--accent) 40%,transparent)}.note{min-height:3em}
.step{background:linear-gradient(150deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:16px;padding:20px;min-height:140px}.progress{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0}
[hidden]{display:none!important}@keyframes arrive{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
.film,.film *{animation:none!important;transition:none!important}html.film{font-size:24px}.film body{overflow:hidden;width:1920px;height:1080px}.film .compare,.film .map{aspect-ratio:auto;height:210px}.film .detail{padding:36px 48px}.film .detail>h3:nth-last-of-type(1),.film .detail>h3:nth-last-of-type(1)+p,.film [data-back],.film [data-next-step]{display:none}.film header,.film main,.film footer{max-width:none;padding-inline:96px}.film main{position:relative}.film main>section{position:absolute;inset:0 96px auto 96px}.film footer{display:none}.film .chapters{display:none}.film .row{display:none}
'''

DECK_JS = r'''
(function(){
const menu=document.getElementById('menu'),panels=[...document.querySelectorAll('.detail')],chapters=[...document.querySelectorAll('[data-chapter]')],live=document.getElementById('live');
function mark(n){chapters.forEach((b,j)=>b.setAttribute('aria-current',j===n?'true':'false'))}
function open(i,push){i=(i+panels.length)%panels.length;menu.hidden=true;panels.forEach((p,j)=>p.hidden=j!==i);mark(i+1);panels[i].focus();live.textContent=panels[i].dataset.title;if(push!==false)history.replaceState(null,'','#service-'+(i+1));}
function back(){const was=panels.findIndex(p=>!p.hidden);panels.forEach(p=>p.hidden=true);menu.hidden=false;mark(0);live.textContent=document.title;history.replaceState(null,'',location.pathname+location.search);(document.querySelector('[data-open="'+Math.max(was,0)+'"]')||menu).focus();}
document.addEventListener('click',e=>{const t=e.target.closest('[data-open],[data-back],[data-go],[data-chapter],[data-next-step],[data-pin]');if(!t)return;
 if(t.dataset.open!==undefined)open(+t.dataset.open);else if(t.dataset.back!==undefined)back();else if(t.dataset.go!==undefined){const i=panels.findIndex(p=>!p.hidden);open(i+ +t.dataset.go);}
 else if(t.dataset.chapter!==undefined){+t.dataset.chapter===0?back():open(+t.dataset.chapter-1);}
 else if(t.dataset.nextStep!==undefined){const box=t.closest('.demo'),items=[...box.querySelectorAll('.steps li')],n=items.filter(x=>x.classList.contains('on')).length;if(n>=items.length){items.forEach(x=>x.classList.remove('on'));t.textContent=t.dataset.labelNext;return;}items[n].classList.add('on');if(n+1>=items.length)t.textContent=t.dataset.labelRestart;}
 else if(t.dataset.pin!==undefined){const box=t.closest('.demo');box.querySelectorAll('.pin').forEach(p=>p.setAttribute('aria-pressed',p===t?'true':'false'));box.querySelector('.note').textContent=t.dataset.note;}
});
document.addEventListener('input',e=>{if(e.target.matches('.compare input')){const pos=e.target.value+'%';e.target.closest('.compare').style.setProperty('--pos',pos);e.target.setAttribute('aria-valuetext',e.target.value+' %');}});
window.addEventListener('keydown',e=>{if(e.target.matches('input'))return;const i=panels.findIndex(p=>!p.hidden);if(e.key==='Escape'&&i>=0)back();if(i>=0&&e.key==='ArrowRight')open(i+1);if(i>=0&&e.key==='ArrowLeft')open(i-1);});
const m=location.hash.match(/^#service-(\d+)$/);if(m&&+m[1]>=1&&+m[1]<=panels.length)open(+m[1]-1,false);else mark(0);
// Film mode: pure function of t, nothing kept between frames
if(!window.__RENDERING__)return;
document.documentElement.classList.add('film');
const sections=[menu,...panels],HOLD=DUR,FADE=.45,clamp=(v)=>Math.min(1,Math.max(0,v)),out=(p)=>1-Math.pow(1-p,3);
sections.forEach(s=>{s.hidden=false;s.style.willChange='transform,opacity'});
window.COMP={width:1920,height:1080,fps:30,duration:sections.length*HOLD};
window.seek=function(t){const cur=Math.min(sections.length-1,Math.floor(t/HOLD)),local=t-cur*HOLD;
 sections.forEach((s,j)=>{const on=j===cur,enter=out(clamp(local/FADE)),leave=clamp((HOLD-local)/.3),a=on?Math.min(enter,cur===sections.length-1?1:leave):0;
  s.style.opacity=a;s.style.visibility=a>0?'visible':'hidden';s.style.transform=on?'translateY('+(1-enter)*36+'px) scale('+(1+local*.004)+')':'none';
  s.querySelectorAll('.tile,.steps li,ul.benefits li').forEach((el,k)=>{const p=out(clamp((local-.25-k*.12)/.4));el.style.opacity=on?p:0;el.style.transform='translateY('+(1-p)*24+'px)';});
  const bar=s.querySelector('.compare');if(bar)bar.style.setProperty('--pos',(on?20+60*clamp((local-.6)/(HOLD-1.2)):50)+'%');});};
window.seek(0);
})();'''


def _demo(s: dict, t: dict, idx: int) -> str:
    out = ''
    ba = s.get('before_after')
    if ba:
        out += (f'<h3>{esc(t["compare"])}</h3><div class="compare demo"><div class="side a"><span><b>{esc(t["before"])}</b>{esc(ba.get("before", ""))}</span></div>'
                f'<div class="side b"><span><b>{esc(t["after"])}</b>{esc(ba.get("after", ""))}</span></div><div class="bar"></div>'
                f'<input type="range" min="0" max="100" value="50" aria-label="{esc(t["compare"])}"></div>')
    steps = s.get('steps')
    if steps:
        items = ''.join(f'<li><strong>{esc(x.get("title", ""))}</strong>{esc(x.get("text", ""))}</li>' for x in steps)
        out += (f'<div class="demo"><h3>{esc(t["steps"])}</h3><ol class="steps">{items}</ol><button type="button" data-next-step data-label-next="{esc(t["step"])}" '
                f'data-label-restart="{esc(t["restart"])}">{esc(t["step"])}</button></div>')
    pins = s.get('hotspots')
    if pins:
        btn = ''.join(f'<button type="button" class="pin" style="left:{float(p.get("x", 50)):.1f}%;top:{float(p.get("y", 50)):.1f}%" data-pin aria-pressed="false" '
                      f'data-note="{esc(p.get("note", ""))}" aria-label="{esc(p.get("label", ""))}"></button>' for p in pins)
        out += f'<div class="demo"><h3>{esc(t["points"])}</h3><div class="map">{btn}</div><p class="note" aria-live="polite"></p></div>'
    return out


def presentation(spec: dict, output: Path) -> dict:
    services = spec.get('services', [])
    if not isinstance(services, list) or not services:
        raise ValueError('Déclarer services: liste non vide')
    t = TEXT.get(spec.get('language', 'fr'), TEXT['fr'])
    title, brand = spec.get('title', t['menu']), spec.get('brand', 'Studio')
    nav = f'<nav aria-label="{esc(t["chapters"])}"><ol class="chapters"><li><button type="button" data-chapter="0">{esc(t["menu"])}</button></li>'
    nav += ''.join(f'<li><button type="button" data-chapter="{i + 1}">{i + 1}. {esc(s.get("title", ""))}</button></li>' for i, s in enumerate(services)) + '</ol></nav>'
    body = f'<div id="live" class="sr" aria-live="polite" style="position:absolute;left:-9999px"></div><section id="menu" aria-label="{esc(t["menu"])}"><p class="eyebrow">{esc(t["menu"])}</p><h1>{esc(title)}</h1>'
    if spec.get('subtitle'):
        body += f'<p>{esc(spec["subtitle"])}</p>'
    body += '<div class="grid">'
    for i, s in enumerate(services):
        name = s.get('title', f'{t["tag"]} {i + 1}')
        body += (f'<article class="tile"><p class="tag">{esc(t["tag"])} {i + 1}</p><h2>{esc(name)}</h2><p>{esc(s.get("summary", ""))}</p>'
                 f'<button type="button" class="primary" data-open="{i}" aria-label="{esc(t["more"])} : {esc(name)}">{esc(t["more"])}</button></article>')
    body += '</div></section>'
    for i, s in enumerate(services):
        name = s.get('title', f'{t["tag"]} {i + 1}')
        body += (f'<section id="detail-{i}" class="detail" hidden tabindex="-1" data-title="{esc(name)}" aria-label="{esc(name)}"><button type="button" data-back>{esc(t["back"])}</button>'
                 f'<p class="tag" style="margin-top:18px">{esc(t["tag"])} {i + 1}</p><h2>{esc(name)}</h2><p>{esc(s.get("description", s.get("summary", "")))}</p>')
        if s.get('benefits'):
            body += f'<h3>{esc(t["benefits"])}</h3><ul class="benefits">' + ''.join(f'<li>{esc(x)}</li>' for x in s['benefits']) + '</ul>'
        body += _demo(s, t, i)
        body += f'<h3>{esc(t["price"])}</h3><p>{esc(s["price"]) if s.get("price") else esc(t["ask"])}</p>'
        link = s.get('url', '')
        if link and re.match(r'^https?://', link, re.I):
            body += f'<p><a class="cta" href="{esc(link)}" target="_blank" rel="noopener noreferrer">{esc(t["more"])}</a></p>'
        body += f'<div class="row"><button type="button" data-go="-1">{esc(t["prev"])}</button><button type="button" data-go="1">{esc(t["next"])}</button></div></section>'
    script = DECK_JS.replace('DUR', str(float(spec.get('film_seconds_per_scene', 3.5))))
    page = ('<!doctype html><html lang="' + t['lang'] + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>' + esc(title) + '</title><style>' + CSS.replace('ACCENT', color(spec.get('accent', '#7c6cff'))) + '</style></head><body>'
            '<header><div class="brand">' + esc(brand) + '</div>' + nav + '</header><main>' + body + '</main><footer>' + esc(t['foot']) + '</footer>'
            '<script>' + script + '</script></body></html>')
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding='utf-8')
    return {'output': str(output), 'services': len(services), 'interactive': True, 'bytes': output.stat().st_size}


def infographic(spec: dict, output: Path) -> dict:
    steps = spec.get('steps', [])
    if not isinstance(steps, list) or not steps:
        raise ValueError('Déclarer steps: liste non vide')
    t = TEXT.get(spec.get('language', 'fr'), TEXT['fr'])
    title, brand = spec.get('title', t['infotag']), spec.get('brand', 'Infographic Studio')
    body = f'<p class="eyebrow">{esc(t["infotag"])}</p><h1>{esc(title)}</h1><p>{esc(spec.get("intro", ""))}</p><div class="progress" role="group">'
    for i, s in enumerate(steps):
        body += f'<button type="button" class="step-nav" data-step="{i}" aria-current="{"step" if i == 0 else "false"}">{i + 1} · {esc(s.get("title", str(i + 1)))}</button>'
    body += '</div>'
    for i, s in enumerate(steps):
        body += f'<section class="step" id="step-{i}" {"" if i == 0 else "hidden"} tabindex="-1" aria-label="{esc(t["stepl"])} {i + 1}"><p class="tag">{esc(t["stepl"])} {i + 1} / {len(steps)}</p><h2>{esc(s.get("title", ""))}</h2><p>{esc(s.get("description", ""))}</p>'
        if 'value' in s:
            body += f'<strong style="font-size:clamp(2rem,5vw,4rem);color:#c5bdff">{esc(s["value"])}</strong><p>{esc(s.get("unit", ""))}</p>'
        body += '</section>'
    body += f'<p><button class="primary" id="next" type="button">{esc(t["step"])} →</button></p>'
    if spec.get('source'):
        body += f'<p><small>{esc(t["source"])} : {esc(spec["source"])}</small></p>'
    script = r'''(function(){const steps=[...document.querySelectorAll('.step')],buttons=[...document.querySelectorAll('.step-nav')];let n=0;
function show(i){n=(i+steps.length)%steps.length;steps.forEach((s,j)=>s.hidden=j!==n);buttons.forEach((b,j)=>b.setAttribute('aria-current',j===n?'step':'false'));steps[n].focus();}
buttons.forEach((b,i)=>b.addEventListener('click',()=>show(i)));document.getElementById('next').addEventListener('click',()=>show(n+1));
window.addEventListener('keydown',e=>{if(e.key==='ArrowRight')show(n+1);if(e.key==='ArrowLeft')show(n-1)});})();'''
    page = ('<!doctype html><html lang="' + t['lang'] + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + esc(title) + '</title><style>'
            + CSS.replace('ACCENT', color(spec.get('accent', '#7c6cff'))) + '</style></head><body><header><div class="brand">' + esc(brand) + '</div></header><main>' + body + '</main><footer>' + esc(t['foot']) + '</footer><script>' + script + '</script></body></html>')
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding='utf-8')
    return {'output': str(output), 'steps': len(steps), 'interactive': True, 'bytes': output.stat().st_size}
