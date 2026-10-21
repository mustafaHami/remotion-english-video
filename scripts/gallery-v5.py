from pathlib import Path
import json,html
ROOT=Path(__file__).resolve().parents[1]
config=json.loads((ROOT/'src/archive/experiments/options-v5/render-config.json').read_text(encoding='utf-8'))
cards=[]
for c in config:
    n=c['option'];folder=f'test-option-{n}'
    cards.append(f'<article><h2>Option {n} — {html.escape(c["title"])}</h2><video controls playsinline preload="none" poster="{folder}/captures-v5/frame-045.png" src="{folder}/{folder}-v5.mp4"></video><p>{c["frames"]//30} secondes · <a href="{folder}/{folder}-v5.mp4">Ouvrir la vidéo</a></p></article>')
page='''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>V5 — essais avec le renard</title><style>*{box-sizing:border-box}body{background:#F3F0FD;color:#1E1B3A;font-family:system-ui;margin:0}main{max-width:1200px;margin:auto;padding:24px}h1{font-size:28px}section{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:24px}article{background:#FFFDF8;border:2px solid #1E1B3A;border-radius:22px;overflow:hidden;box-shadow:0 4px #1E1B3A}h2,p{padding:0 16px}h2{font-size:18px;min-height:44px}video{width:100%;display:block}a{color:#6A3FD1}</style><main><h1>Trois essais avec le renard</h1><p>Accueil parlé, exercice, félicitations en vert et au revoir animé. Phase de test.</p><section>'''+''.join(cards)+'''</section><p><a href="index-v4.html">Comparer avec les essais précédents</a></p></main><script>document.querySelectorAll('video').forEach(v=>v.addEventListener('play',()=>document.querySelectorAll('video').forEach(other=>{if(other!==v)other.pause()})))</script></html>'''
out=ROOT/'output/tests'
(out/'index-v5.html').write_text(page,encoding='utf-8')
(out/'index.html').write_text(page,encoding='utf-8')
