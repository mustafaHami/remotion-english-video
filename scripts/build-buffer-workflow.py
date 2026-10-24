#!/usr/bin/env python3
"""Workflow Buffer visible, limité aux brouillons ; aucun compte ni secret exporté."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def node(id,name,kind,x,parameters,version=4.2,**extra):
    return dict(id=id,name=name,type='n8n-nodes-base.'+kind,typeVersion=version,position=[x,0],parameters=parameters,**extra)
def http(id,name,url,body,x,**extra):
    return node(id,name,'httpRequest',x,{'method':'POST','url':url,'authentication':'genericCredentialType',
        'genericAuthType':'httpHeaderAuth','sendBody':True,'specifyBody':'json','jsonBody':body,
        'options':{'timeout':120000,'redirect':{'redirect':{'followRedirects':False}}}},**extra)
trigger=node('buffer-trigger','Demande de brouillon autorisée','webhook',0,
    {'httpMethod':'POST','path':'REQUIRES-PRIVATE-PATH','authentication':'headerAuth','responseMode':'lastNode','options':{}},2.1)
claim=http('buffer-claim','Réserver une seule création','http://REQUIRES-BRIDGE-CONFIGURATION/buffer/drafts/claim',
    '={{ JSON.stringify({jobId:$json.body.jobId,revision:$json.body.revision,channelId:$json.body.channelId,dispatchId:String($execution.id)}) }}',300,retryOnFail=False)
split=node('buffer-split','Brouillon réservé','splitOut',600,
    {'fieldToSplitOut':'requests','include':'noOtherFields','options':{'destinationFieldName':'draft'}},1)
send=http('buffer-create','Buffer — créer uniquement un brouillon','https://api.buffer.com',
    '={{ JSON.stringify($json.draft.request) }}',900,retryOnFail=False)
send['parameters']['options']['response']={'response':{'neverError':True,'responseFormat':'json'}}
receipt=http('buffer-receipt','Conserver le résultat sans publier','http://REQUIRES-BRIDGE-CONFIGURATION/buffer/drafts/receipt',
    '={{ JSON.stringify({jobId:$("Brouillon réservé").item.json.draft.jobId,revision:$("Brouillon réservé").item.json.draft.revision,channelId:$("Brouillon réservé").item.json.draft.channelId,dispatchId:$("Brouillon réservé").item.json.draft.dispatchId,response:$json}) }}',1200,
    retryOnFail=True,maxTries=3,waitBetweenTries=2000)
nodes=[trigger,claim,split,send,receipt]
connections={a['name']:{'main':[[{'node':b['name'],'type':'main','index':0}]]} for a,b in zip(nodes,nodes[1:])}
guard=node('buffer-has-request','Une création reste nécessaire','if',470,{
    'conditions':{'options':{'typeValidation':'strict','version':2},'conditions':[
        {'id':'prepared','leftValue':'={{ $json.requests.length > 0 }}','rightValue':True,
         'operator':{'type':'boolean','operation':'true','singleValue':True}}],'combinator':'and'},'options':{}},2.2)
duplicate=node('buffer-duplicate','Brouillon déjà traité — aucun nouvel envoi','noOp',750,{},1)
duplicate['position']=[750,250]
def link(n):return {'node':n['name'],'type':'main','index':0}
connections[claim['name']]={'main':[[link(guard)]]}
connections[guard['name']]={'main':[[link(split)],[link(duplicate)]]}
nodes.extend([guard,duplicate])
note=node('buffer-note','Limites et reprise','stickyNote',0,{'content':
    '## Brouillons Buffer uniquement\nWebhook authentifié, aucun horaire et aucun Telegram Trigger. '
    'Le bridge exige une vidéo validée et une destination préparée explicitement. '
    'La requête GraphQL impose saveToDraft=true, sans dueAt. '
    'Une réservation SQLite empêche les doublons même après redémarrage. '
    'Aucune relance automatique de Buffer : un résultat inconnu nécessite une réconciliation. '
    'Les reçus et notifications sont persistés ; aucun statut shared ni accord de publication créé. '
    'Exécutions non conservées pour protéger l’en-tête du webhook. Les erreurs restent visibles dans les états durables.',
    'width':1000,'height':240},1)
note['position']=[0,-300];nodes.append(note)
workflow={'name':'Englizy — Brouillons Buffer (sans publication)','nodes':nodes,'connections':connections,
    'settings':{'executionOrder':'v1','timezone':'Europe/Paris','saveDataSuccessExecution':'none',
                'saveDataErrorExecution':'none','saveExecutionProgress':False,'saveManualExecutions':False}}
(ROOT/'deploy/n8n/workflows/buffer-drafts.json').write_text(json.dumps(workflow,ensure_ascii=False,indent=2)+'\n')
print('Export Buffer sans secret créé.')
