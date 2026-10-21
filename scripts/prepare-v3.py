"""Create deterministic narration cues and test configuration from shared lesson data."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'src/archive/experiments/options-v3'
data=json.loads((SRC/'content.json').read_text(encoding='utf-8'))
rows=json.loads((ROOT/'src/archive/experiments/test-option-1/rows.json').read_text(encoding='utf-8'))
old=json.loads((ROOT/'src/archive/experiments/options/render-config.json').read_text(encoding='utf-8'))
jobs=[];config=[]
def say(option,text,start):jobs.append({'option':option,'text':text,'start':start})
for n in range(1,15):
    old_item=next((i for i in old if i['option']==n),None)
    frames=1950 if n==1 else 1290 if n==3 else 1260
    captures=[120,255,650,1050,1500,1920] if n==1 else [120,250,540,670,960,frames-30]
    if n==2:captures=[120,360,530,800,1100,1230]
    if n==9:captures=[120,280,450,595,910,1230]
    config.append({'key':str(n),'option':n,'verb':'be','id':f'TestOption{n}-V3','name':old_item['name'] if old_item else 'Présent, passé, futur','title':old_item['title'] if old_item else 'Présent, passé, futur.','frames':frames,'captures':captures,'completeAt':1770 if n==1 else frames-90})
for family in data['verbSeries'][1:]:
    key='2-'+family['verb']
    config.append({'key':key,'option':2,'verb':family['verb'],'id':f'TestOption2-{family["verb"]}-V3','name':'Un verbe et ses pronoms : '+family['verb'],'title':family['label'],'frames':1260,'captures':[120,360,530,800,1100,1230],'completeAt':1170})
    for i,form in enumerate(family['forms']):say(key,form+'.',72+i*48)
    for i,example in enumerate(family['examples']):say(key,example['en'],450+i*270+65)
for i,row in enumerate(rows):
    say(1,f'{row["present"]}. {row["past"]}.',210+i*75+6)
    say(1,row['future']+'.',1140+i*60+12)
for i,form in enumerate(data['verbSeries'][0]['forms']):say(2,form+'.',72+i*48)
for i,example in enumerate(data['verbExamples']):say(2,example['en'],450+i*270+65)
opposites=[['big','small'],['hot','cold'],['fast','slow'],['open','closed'],['happy','sad'],['near','far'],['light','dark'],['full','empty'],['early','late'],['strong','weak']]
for i,(a,b) in enumerate(opposites):say(3,f'{a}. {b}.',210+i*90+18)
for n,key in [(4,'gap'),(5,'situation'),(6,'contrast'),(8,'corrections'),(11,'recall'),(12,'transfer')]:
    for i,example in enumerate(data[key]):say(n,example['en'],420*i+(95 if n==12 and i==0 else 235))
for i,item in enumerate(data['associations']):
    for n in [7,13]:
        start=420*i if n==7 else 30+390*i
        say(n,item['verb']+' '+item['rest']+'.',start+125)
        say(n,item['en'],start+235)
for i,line in enumerate(data['dialogue']):say(9,line['en'],(i//2)*315+(45 if i%2==0 else 195))
for i,line in enumerate(data['listen']):
    for start in [55,310]:say(10,line['en'],420*i+start)
for i,item in enumerate(data['phrasal']):
    say(14,item['phrase']+'.',420*i+160)
    say(14,item['en'],420*i+275)
(SRC/'render-config.json').write_text(json.dumps(config,indent=2,ensure_ascii=False),encoding='utf-8')
(SRC/'narration-jobs.json').write_text(json.dumps(jobs,indent=2,ensure_ascii=False),encoding='utf-8')
print(len(config),'tests;',len(jobs),'narration cues')
