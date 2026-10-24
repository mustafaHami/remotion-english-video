#!/usr/bin/env python3
"""Workflow natif de publication autorisée et suivi par lecture sans renvoi."""
import json
from pathlib import Path
import runpy
ROOT=Path(__file__).resolve().parents[1]
b=runpy.run_path(str(ROOT/'scripts/build-buffer-workflow.py'));node,http=b['node'],b['http']
timer=node('publication-timer','Suivre les accords et résultats','scheduleTrigger',0,{'rule':{'interval':[{'field':'minutes','minutesInterval':1}]}},1.2)
webhook=node('publication-webhook','Contrôle opérateur authentifié','webhook',0,{'httpMethod':'POST','path':'REQUIRES-PRIVATE-PATH','authentication':'headerAuth','responseMode':'lastNode','options':{}},2.1);webhook['position']=[0,250]
claim=http('publication-claim','Réserver les lectures nécessaires','http://REQUIRES-BRIDGE-CONFIGURATION/buffer/publications/claim','{}',250,retryOnFail=False)
split=node('publication-read-split','Lecture réservée','splitOut',700,{'fieldToSplitOut':'reads','include':'noOtherFields','options':{'destinationFieldName':'reading'}},1)
read=http('publication-read','Buffer — relire le brouillon ou le résultat','https://api.buffer.com','={{ JSON.stringify($json.reading.request) }}',950,retryOnFail=True,maxTries=3,waitBetweenTries=2000)
preflight=http('publication-preflight','Vérifier accord et contenu avant envoi','http://REQUIRES-BRIDGE-CONFIGURATION/buffer/publications/preflight',
    '={{ JSON.stringify({postId:$("Lecture réservée").item.json.reading.postId,response:$json,dispatchId:String($execution.id)}) }}',1200,retryOnFail=False)
mutations=node('publication-mutation-split','Publication réservée une seule fois','splitOut',1650,{'fieldToSplitOut':'mutations','include':'noOtherFields','options':{'destinationFieldName':'publishing'}},1)
send=http('publication-send','Buffer — publier la version autorisée','https://api.buffer.com','={{ JSON.stringify($json.publishing.request) }}',1900,retryOnFail=False)
send['parameters']['options']['response']={'response':{'neverError':True,'responseFormat':'json'}}
receipt=http('publication-receipt','Conserver le résultat de la demande','http://REQUIRES-BRIDGE-CONFIGURATION/buffer/publications/receipt',
    '={{ JSON.stringify({postId:$("Publication réservée une seule fois").item.json.publishing.postId,dispatchId:$("Publication réservée une seule fois").item.json.publishing.dispatchId,response:$json}) }}',2150,retryOnFail=True,maxTries=3,waitBetweenTries=2000)
def guard(id,name,field,x):
 return node(id,name,'if',x,{'conditions':{'options':{'typeValidation':'strict','version':2},'conditions':[{'id':id,'leftValue':'={{ $json.'+field+'.length > 0 }}','rightValue':True,'operator':{'type':'boolean','operation':'true','singleValue':True}}],'combinator':'and'},'options':{}},2.2)
read_guard=guard('publication-has-read','Une lecture est nécessaire','reads',480)
mutation_guard=guard('publication-has-mutation','Une publication est autorisée','mutations',1430)
idle=node('publication-idle','Aucun nouvel envoi nécessaire','noOp',1200,{},1);idle['position']=[1200,350]
def link(n):return {'node':n['name'],'type':'main','index':0}
connections={}
for a,z in [(timer,claim),(webhook,claim),(claim,read_guard),(split,read),(read,preflight),(preflight,mutation_guard),(mutations,send),(send,receipt)]:connections[a['name']]={'main':[[link(z)]]}
connections[read_guard['name']]={'main':[[link(split)],[link(idle)]]}
connections[mutation_guard['name']]={'main':[[link(mutations)],[link(idle)]]}
note=node('publication-note','Accord exact et reprise','stickyNote',0,{'width':1200,'height':240,'content':
 '## Publication uniquement après accord explicite\nUn accord lie tâche, version, SHA-256, légendes, réglages, comptes et identifiants des brouillons. '
 'PUBLISH_ENABLED=true est aussi requis. La lecture Buffer compare le contenu avant la mutation editPost shareNow. '
 'Réservation durable avant mutation, aucun retry de publication. Les relances suivantes lisent uniquement les résultats. '
 'Lecture espacée progressivement, huit contrôles maximum avant intervention. Un résultat partiel garde la tâche ouverte. '
 'Seuls sent + sentAt + mode automatique sur toutes les destinations autorisent shared et Excel. '
 'Le minuteur technique ne crée aucune vidéo ni accord ; sans tâche autorisée il ne contacte pas Buffer.'},1);note['position']=[0,-300]
value={'name':'Englizy — Publication autorisée et suivi Buffer','nodes':[timer,webhook,claim,read_guard,split,read,preflight,mutation_guard,mutations,send,receipt,idle,note],'connections':connections,
 'settings':{'executionOrder':'v1','timezone':'Europe/Paris','saveDataSuccessExecution':'none','saveDataErrorExecution':'none','saveExecutionProgress':False,'saveManualExecutions':False}}
(ROOT/'deploy/n8n/workflows/buffer-publication.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print('Workflow publication générique créé, inactif tant qu’il n’est pas installé.')
