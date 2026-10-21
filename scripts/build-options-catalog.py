"""Index the existing local test videos without changing their media files."""
from pathlib import Path
import json,html,re
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/tests'
config=json.loads((ROOT/'src/archive/experiments/options/render-config.json').read_text())
items=[{'option':1,'name':'Présent, passé, futur','frames':1590,'video':'test-option-1-v2.mp4','poster':'captures-v2/frame-1589.png','board':'planche-test-option-1-v2.jpg'}]
summaries=[]
for item in config:
    n=item['option'];folder=OUT/f'test-option-{n}'
    video=f'test-option-{n}.mp4'
    assert (folder/video).exists(),f'Video not yet rendered: {n}'
    metadata=json.loads((folder/'qa/metadata.json').read_text())
    records=json.loads((folder/'layout-qa.json').read_text())
    assert len(records)==item['frames'] and not any(r['violations'] or not all(r['fonts']) for r in records)
    summary={'option':n,'frames':len(records),'seconds':item['frames']/30,'layoutErrors':0,'centerErrorPx':round(3*max(r['centerError'] for r in records),5),'fullDecode':True,'bytes':(folder/video).stat().st_size}
    if n==8:summary['correctionContinuity']=json.loads((folder/'qa/correction-continuity.json').read_text())
    if n==10:summary['audio']=json.loads((folder/'qa/audio-qa.json').read_text())
    (folder/'qa/inspection.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    summaries.append(summary)
    item.update(video=video,poster=f'captures/frame-{item["captures"][-1]:03}.png',board=f'planche-test-option-{n}.jpg')
    items.append(item)
    p=folder/'README.md'
    old=p.read_text(encoding='utf-8')
    old=re.sub(r'\*\*Statut\s*:.*?\*\*','**Statut : prototype animé livré ; retour individuel attendu. Base graphique de l’option 1 retenue.**',old,count=1)
    old=re.sub(r'Futur livrable :[^\n]*','Voir la livraison animée et ses captures ci-dessous.',old)
    old=old.replace('Le duo figure déjà dans la v2 globale ; il n\'existe pas encore de vidéo autonome pour cette option.','Le duo figurait déjà dans la v2 globale ; ce dossier contient désormais un essai autonome.')
    old=old.replace('Cet essai figure dans la v2 globale ; aucun nouveau rendu autonome n\'a été créé ici.','Cet essai figurait dans la v2 globale ; ce dossier contient désormais sa variante autonome.')
    old=old.split('\n## Livraison animée — suite validée')[0]
    audio='Avec essai de voix neuronale en-GB-SoniaNeural, à 3s et 14s ; sept secondes de silence pour répéter. Cette voix synthétique reste provisoire.' if n==10 else 'Sans audio pour évaluer ce format visuel.'
    notes={2:'Sept pronoms, flèches tracées et réponses progressives au présent.',3:'Dix paires d’opposés, deux colonnes égales et une ligne active à la fois.',4:'Une seule phrase, deux choix, six secondes de recherche et aucun deuxième exercice.',5:'Ticket de restaurant vectoriel, deux formulations et révélation de la phrase naturelle.',6:'Deux constructions, surlignage de me et repère limité aux exemples montrés.',7:'Deux groupes de mots qui se rapprochent ; une association après l’autre.',8:'Retrait animé de am, puis phrase corrigée accompagnée d’une coche.',9:'Deux répliques en bulles sans personnage, avec traductions différées.',10:'Deux écoutes du même fichier local et onde sonore issue des échantillons audio.',11:'Rappel sans choix, six secondes de recherche, puis une réponse possible.',12:'Variante facultative : première association, puis un seul essai de transfert. Pas une étape obligatoire des autres formats.',13:'Fiche récapitulative construite progressivement avec deux objets SVG.',14:'Ajout de off à get, puis flèche de sortie d’un bus ; un seul sens en contexte.'}[n]
    old+=f'\n## Livraison animée — suite validée\n\n- [Vidéo de test]({video}) — {item["frames"]/30:g} s, 1080 × 1920, 30 i/s.\n- [Planche issue du MP4]({item["board"]}).\n- Captures : captures/ ; contrôle de mise en page : layout-qa.json ; métadonnées et mouvements : qa/.\n\n{notes}\n\n{audio}\n\nModèle partagé dans src/templates/ et contenu dans src/archive/experiments/options/data.ts. Rendre cette seule option : `npm run render:options -- --options={n}`. Inspecter : `python scripts/inspect-options.py --options={n}`.\n\nToujours une expérience du même projet ; aucune publication. Les contrôles techniques et l’inspection par images ne remplacent pas ton retour sur le rythme et le design.\n'
    p.write_text(old,encoding='utf-8')
rows=[];cards=[]
for item in items:
    n=item['option'];base=f'test-option-{n}'
    rows.append(f'| [{n} — {item["name"]}]({base}/README.md) | [{item["frames"]/30:g} s]({base}/{item["video"]}) | [Planche]({base}/{item["board"]}) |')
    cards.append(f'<article id="option-{n}"><header><span>OPTION {n:02}</span><h2>{html.escape(item["name"])}</h2></header><video controls playsinline preload="none" poster="{base}/{item["poster"]}" src="{base}/{item["video"]}"></video><footer><span>{item["frames"]/30:g} secondes'+(' · avec voix d’essai' if n==10 else ' · silencieux')+f'</span><a href="{base}/{item["video"]}">Ouvrir la vidéo</a><a href="{base}/{item["board"]}">Voir la planche</a></footer></article>')
index='''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Les 14 options — essais vidéo</title><style>
*{box-sizing:border-box}body{margin:0;background:#F3F0FD;color:#1E1B3A;font-family:system-ui,sans-serif}main{max-width:1320px;margin:auto;padding:36px 24px}h1{font-size:32px;margin:10px 0}p{line-height:1.6;max-width:820px}nav{display:flex;gap:8px;flex-wrap:wrap;margin:26px 0}nav a{border:1px solid #1E1B3A;border-radius:50%;height:36px;width:36px;display:grid;place-items:center;background:#FFD84D;text-decoration:none}a{color:#6A3FD1}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:24px}article{background:#FFFDF8;border:2px solid #1E1B3A;border-radius:22px;overflow:hidden;box-shadow:0 4px 0 #1E1B3A;scroll-margin:20px}header{padding:18px;min-height:100px}header span{font-size:11px;font-weight:800;letter-spacing:.15em}h2{font-size:18px;margin:7px 0 0}video{width:100%;aspect-ratio:9/16;background:#A99BFF;display:block}footer{padding:16px;display:flex;flex-wrap:wrap;gap:10px;font-size:13px}footer span{width:100%}aside{padding:14px 18px;background:#DDF5EC;border-radius:14px;margin:20px 0}
</style></head><body><main><h1>Les 14 options, à regarder une à une.</h1><p>La base graphique de l’option 1 est retenue. Ces vidéos explorent maintenant les différentes façons de présenter un exercice. Tu peux ouvrir chaque vidéo, regarder sa planche et donner tes retours par numéro.</p><aside>L’option 10 contient une voix synthétique d’essai. Les autres vidéos sont silencieuses. Nous restons en phase de test.</aside><nav>'''+''.join(f'<a href="#option-{i}" aria-label="Option {i}">{i}</a>' for i in range(1,15))+'''</nav><section class="grid">'''+''.join(cards)+'''</section></main><script>document.querySelectorAll('video').forEach(v=>v.addEventListener('play',()=>document.querySelectorAll('video').forEach(other=>{if(other!==v)other.pause()})))</script></body></html>'''
(OUT/'index.html').write_text(index,encoding='utf-8')
(OUT/'options-render-summary.json').write_text(json.dumps(summaries,indent=2),encoding='utf-8')
readme='''# Catalogue des 14 options de test

La V2 de l’option 1 est retenue comme base graphique. L’utilisateur a autorisé la suite sur les autres vues. Les options 2–14 ont chacune leur prototype dans le même projet Remotion ; retour individuel attendu. Aucun épisode publié.

[Ouvrir la galerie vidéo locale](index.html)

| Option | Vidéo | Aperçu |
| --- | --- | --- |
'''+ '\n'.join(rows)+'''

Chaque dossier contient le MP4, six captures, une planche de six poses et les contrôles. L’option 1 conserve ses douze captures et ses archives. Les anciens essais restent disponibles pour l’historique.

La présentation privilégie une carte centrée, les textes sur une ligne, un foyer d’attention et des révélations progressives. Le second essai est limité à l’option 12, variante facultative. Les tableaux ont sept pronoms ou dix paires ; les vidéos centrées sur une phrase ne sont pas allongées artificiellement à dix éléments.

L’option 10 contient une voix neuronale provisoire et deux écoutes avec sept secondes de silence pour répéter. La voix finale reste à choisir. Les autres essais sont silencieux.

Relancer tout le nouveau lot : `npm run render:options`. Une seule option : `npm run render:options -- --options=3`. Contrôle des exports : `npm run inspect:options`. Les planches de contrôle temporel proviennent des MP4 décodés ; aucune lecture humaine continue à vitesse réelle n’est attestée.
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
p=OUT/'test-option-1/README.md'
text=p.read_text(encoding='utf-8').replace('**Version actuelle : v2, dix verbes et centrage sur toute l\'image. Prototype en phase de test, à valider.**','**Version actuelle : v2, dix verbes et centrage sur toute l’image. Base graphique retenue par l’utilisateur pour poursuivre les autres vues ; le projet reste en phase de test.**')
text=text.replace('**L\'essai se limite à l\'option 1. Les options 2–14 attendent la validation du design et une nouvelle étape de production.**','**La base graphique de cet essai est retenue pour poursuivre les options 2–14. Les nouveaux prototypes sont livrés dans leurs dossiers et attendent leurs retours individuels.**')
p.write_text(text,encoding='utf-8')
# A single image makes visual comparison possible without opening fourteen files.
board=Image.new('RGB',(5*220,3*426),'#E9E7ED');draw=ImageDraw.Draw(board)
for i,item in enumerate(items):
    n=item['option'];im=Image.open(OUT/f'test-option-{n}'/item['poster']).convert('RGB').resize((216,384))
    x=(i%5)*220+2;y=(i//5)*426+24;board.paste(im,(x,y));draw.text((x,y-18),f'Option {n:02} / {item["frames"]/30:g}s',fill='#1E1B3A')
board.save(OUT/'apercu-14-options.jpg',quality=94)
print('Local gallery, 14-option overview and per-option READMEs ready.')
