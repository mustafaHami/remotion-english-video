"""Publish the reviewed V3 tests in a local gallery, preserving the previous catalog."""
from pathlib import Path
import json,html,shutil
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/tests'
config=json.loads((ROOT/'src/archive/experiments/options-v3/render-config.json').read_text(encoding='utf-8'))
config.sort(key=lambda c:c['option']*10+({'be':0,'have':1,'can':2,'could':3}.get(c['verb'],0) if c['option']==2 else 0))
cards=[];rows=[];reports=[]
for item in config:
    n=item['option'];key=item['key'];suffix='-v3'+('-'+item['verb'] if '-' in key else '')
    folder=OUT/f'test-option-{n}';stem=f'test-option-{n}{suffix}'
    report=json.loads((folder/f'qa{suffix}/inspection.json').read_text(encoding='utf-8'))
    assert report['layoutErrors']==0 and report['fullVideoDecode'] and report['fullAudioDecode']
    assert (folder/f'{stem}.mp4').stat().st_size==report['bytes'],'The inspection report is stale'
    reports.append(report)
    video=f'{stem}.mp4';board=f'planche-{stem}.jpg';poster=f'captures{suffix}/frame-{item["captures"][-1]:03}.png'
    base=f'test-option-{n}';label=f'{n} · {item["verb"]}' if n==2 else str(n)
    rows.append(f'| [{label} — {item["name"]}]({base}/{video}) | {item["frames"]/30:g} s | [Aperçu]({base}/{board}) |')
    name={'1':'Présent, passé, futur','2':'Be : les formes et trois usages','2-have':'Have : les formes et trois usages','2-can':'Can : une forme, trois usages','2-could':'Could : la capacité dans le passé','3':'Dix paires d’opposés','4':'Trois phrases à compléter','5':'Trois phrases au restaurant','6':'Say / tell : trois exemples','7':'Trois associations de mots','8':'Trois erreurs à corriger','9':'Une conversation de huit répliques','10':'Trois phrases à écouter et répéter','11':'Trois phrases à retrouver','12':'Un modèle, deux essais','13':'Un mémo de trois expressions','14':'Trois verbes à particule'}[key]
    cards.append(f'<article id="test-{key}"><header><span>OPTION {html.escape(label)} · V3</span><h2>{html.escape(name)}</h2></header><video controls playsinline preload="none" poster="{base}/{poster}" src="{base}/{video}"></video><footer><span>{item["frames"]/30:g} secondes · avec prononciation</span><a href="{base}/{video}">Ouvrir la vidéo</a><a href="{base}/{board}">Voir la planche</a></footer></article>')
    readme=folder/'README.md'
    old=readme.read_text(encoding='utf-8')
    marker='<!-- V3-CURRENT -->';end='<!-- /V3-CURRENT -->'
    if marker in old:old=old.split(end,1)[1].lstrip()
    # Add one summary per option below, after collecting all four verb variants.
    item.update(video=video,board=board,poster=poster,nameV3=name)
for n in range(1,15):
    folder=OUT/f'test-option-{n}';p=folder/'README.md';old=p.read_text(encoding='utf-8')
    if '<!-- V3-CURRENT -->' in old:old=old.split('<!-- /V3-CURRENT -->',1)[1].lstrip()
    section='<!-- V3-CURRENT -->\n# Version actuelle — V3 avec voix\n\n'
    for item in (c for c in config if c['option']==n):
        section+=f'- [{item["nameV3"]}]({item["video"]}) — {item["frames"]/30:g} s ; [planche]({item["board"]}).\n'
    section+='\nLa durée cible est celle demandée par l’utilisateur : au moins 35–40 secondes. Cette V3 atteint 42 secondes (43 pour les opposés, 65 pour le tableau). Les exercices courts proposent jusqu’à trois exemples, chacun sur sa carte. Le dialogue comporte huit répliques. Be, have, can et could ont quatre vidéos distinctes dans l’option 2.\n\nPrononciation anglaise intégrée, voix neuronale provisoire en-GB-SoniaNeural. Les recherches se font avant la lecture de la réponse. Nous restons en phase de test. Les versions précédentes ci-dessous sont conservées pour comparaison et leurs anciennes consignes sont remplacées par les retours V3.\n\n<!-- /V3-CURRENT -->\n\n'+old
    p.write_text(section,encoding='utf-8')
style='''*{box-sizing:border-box}body{margin:0;background:#F3F0FD;color:#1E1B3A;font-family:system-ui,sans-serif}main{max-width:1320px;margin:auto;padding:36px 24px}h1{font-size:32px;margin:10px 0}p{line-height:1.6;max-width:850px}nav{display:flex;gap:8px;flex-wrap:wrap;margin:24px 0}nav a{border:1px solid #1E1B3A;border-radius:18px;min-width:38px;padding:8px 12px;background:#FFD84D;text-decoration:none}a{color:#6A3FD1}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:24px}article{background:#FFFDF8;border:2px solid #1E1B3A;border-radius:22px;overflow:hidden;box-shadow:0 4px 0 #1E1B3A;scroll-margin:20px}header{padding:18px;min-height:105px}header span{font-size:11px;font-weight:800;letter-spacing:.1em}h2{font-size:18px;margin:7px 0 0}video{width:100%;aspect-ratio:9/16;background:#A99BFF;display:block}footer{padding:16px;display:flex;flex-wrap:wrap;gap:10px;font-size:13px}footer span{width:100%}aside{padding:14px 18px;background:#DDF5EC;border-radius:14px;margin:20px 0}'''
page='<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>V3 — les essais avec voix</title><style>'+style+'</style></head><body><main><h1>Les essais enrichis, avec prononciation.</h1><p>Trois exemples par format court, huit répliques pour la conversation, et quatre vidéos séparées pour be, have, can et could. La carte et les couleurs restent celles de la base retenue.</p><aside>Toutes les vidéos durent au moins 42 secondes et contiennent la prononciation anglaise. La voix reste provisoire. Nous sommes en phase de test.</aside><nav>'+''.join(f'<a href="#test-{c["key"]}">{c["key"]}</a>' for c in config)+'</nav><section class="grid">'+''.join(cards)+'</section><p><a href="index-v2.html">Comparer avec la galerie précédente</a></p></main><script>document.querySelectorAll("video").forEach(v=>v.addEventListener("play",()=>document.querySelectorAll("video").forEach(other=>{if(other!==v)other.pause()})))</script></body></html>'
if not (OUT/'index-v2.html').exists():shutil.copyfile(OUT/'index.html',OUT/'index-v2.html')
(OUT/'index-v3.html').write_text(page,encoding='utf-8');(OUT/'index.html').write_text(page,encoding='utf-8')
catalog='# Catalogue V3 — essais enrichis avec voix\n\n[Galerie vidéo locale](index-v3.html) · [Comparer avec la V2](index-v2.html)\n\n| Vidéo | Durée | Planche |\n| --- | --- | --- |\n'+'\n'.join(rows)+'\n\nLes vidéos précédentes sont conservées dans les mêmes dossiers. Aucun nouveau projet Remotion ni épisode publié. La voix est provisoire.\n'
(OUT/'catalogue-v3.md').write_text(catalog,encoding='utf-8')
readme=OUT/'README.md';old=readme.read_text(encoding='utf-8')
if not (OUT/'catalogue-v2.md').exists():(OUT/'catalogue-v2.md').write_text(old,encoding='utf-8')
readme.write_text(catalog,encoding='utf-8')
(OUT/'options-v3-summary.json').write_text(json.dumps(reports,indent=2,ensure_ascii=False),encoding='utf-8')
board=Image.new('RGB',(5*220,4*426),'#E9E7ED');draw=ImageDraw.Draw(board)
for j,item in enumerate(config):
    image=Image.open(OUT/f'test-option-{item["option"]}'/item['poster']).convert('RGB').resize((216,384))
    x=(j%5)*220+2;y=(j//5)*426+24;board.paste(image,(x,y));draw.text((x,y-18),f'V3 / {item["key"]} / {item["frames"]/30:g}s',fill='#1E1B3A')
board.save(OUT/'apercu-v3-avec-voix.jpg',quality=94)
print('V3 gallery ready:',len(config),'videos,',sum(r['frames'] for r in reports),'frames,',sum(r['voiceCues'] for r in reports),'voice cues.')
