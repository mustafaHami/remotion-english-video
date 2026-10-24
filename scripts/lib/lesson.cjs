const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const ROOT=path.resolve(__dirname,'../..');
const normalize=s=>s.normalize('NFKC').replace(/\u2019/g,"'").toLowerCase().replace(/[^\p{L}\p{N}]+/gu,' ').trim();
const read=file=>JSON.parse(fs.readFileSync(file,'utf8').replace(/^\uFEFF/,''));
const total=l=>l.timing.introFrames+l.timing.bodyFrames+l.timing.outroFrames;
function spokenContent(l){const d=l.lessonData;switch(l.option){
 case 1:return [...d.rows.map(r=>`${r.present}. ${r.past}.`),...d.rows.map(r=>r.future)];
 case 2:{const family=d.verbSeries.find(v=>v.verb===(l.verb??'be'));return [...family.forms,...(family.examples??d.verbExamples).map(e=>e.en)];}
 case 3:return d.opposites.map(p=>p.join('. '));case 4:return d.gap.map(p=>p.en);case 5:return d.situation.map(p=>p.en);case 6:return d.contrast.map(p=>p.en);
 case 7:case 13:return d.associations.flatMap(p=>[p.verb+' '+p.rest,p.en]);case 8:return d.corrections.map(p=>p.en);case 9:return d.dialogue.map(p=>p.en);case 10:return d.listen.flatMap(p=>[p.en,p.en]);case 11:return d.recall.map(p=>p.en);case 12:return d.transfer.map(p=>p.en);case 14:return d.phrasal.flatMap(p=>[p.phrase,p.en]);default:throw Error('Invalid option');}}
function validate(l,{assets=true}={}){
 if(!Number.isInteger(l.option)||l.option<1||l.option>14)throw Error('Option must be 1..14');
 for(const k of ['title','introText'])if(typeof l[k]!=='string'||!l[k].trim())throw Error('Missing '+k);
 for(const [k,v]of Object.entries(l.timing))if(!Number.isInteger(v)||v<0)throw Error('Invalid timing '+k);
 const t=l.timing,d=l.lessonData,n=l.option;
 const key={1:'rows',2:'verbSeries',3:'opposites',4:'gap',5:'situation',6:'contrast',7:'associations',8:'corrections',9:'dialogue',10:'listen',11:'recall',12:'transfer',13:'associations',14:'phrasal'}[n];
 if(!Array.isArray(d[key]))throw Error('Missing '+key);
 if(n!==2&&d[key].length!==([1,3].includes(n)?10:n===9?8:3))throw Error('Unexpected number of examples for option '+n);
 if([4,5,6,8,11,12].includes(n)&&(t.pageFrames-t.answerAt!==90||t.answerAt-t.pauseAt!==120))throw Error('Quiz must keep four-second search and three-second answer');
 if(n===3&&t.rowFrames!==90)throw Error('Opposites reveal every three seconds');
 const english=l.narration.filter(c=>c.role==='lesson');const expected=spokenContent(l);
 if(expected.length!==english.length||expected.some((s,i)=>normalize(s)!==normalize(english[i].text)))throw Error('Narration does not match current lesson content. Update narration texts, then prepare audio.');
 if([4,6].includes(n))for(const item of d[n===4?'gap':'contrast']){if(!item.choices.includes(item.answer)||normalize(item.before+' '+item.answer+' '+item.after)!==normalize(item.en))throw Error('Visible gap sentence differs from en/answer');}
 if(normalize(l.narration[0].text)!==normalize(l.introText))throw Error('Intro voice differs from introText');
 const clips=l.narration;
 for(let i=0;i<clips.length;i++){
  const c=clips[i];if(!Number.isInteger(c.start)||!Number.isInteger(c.duration)||c.duration<=0||!c.text||!c.voice)throw Error('Incomplete narration cue');
  if(c.start<0||c.start+c.duration>total(l))throw Error('Narration exceeds lesson');
  if(i&&clips[i-1].start+clips[i-1].duration>c.start)throw Error('Overlapping narration');
  if(assets){const p=path.resolve(ROOT,'public',c.src);if(!p.startsWith(path.join(ROOT,'public')+path.sep)||!fs.existsSync(p))throw Error('Missing/unsafe voice asset: '+c.src);
   const hash=crypto.createHash('sha256').update(c.voice+'-5%'+c.text.replace(/\u2019/g,"'")).digest('hex').slice(0,16);
   if(path.basename(p)!==hash+'.wav')throw Error('Stale voice asset for '+c.text);}
 }
 if(n===9&&english.some((c,i)=>c.voice!==(i%2?'en-GB-RyanNeural':'en-GB-SoniaNeural')))throw Error('Dialogue requires alternating Sonia and Ryan');
 if(l.social!==undefined)validateSocial(l.social);
 return l;
}
// Légendes des réseaux : métadonnées de partage, jamais rendues dans la vidéo.
function validateSocial(s){
 if(!s||typeof s!=='object'||Array.isArray(s)||Object.keys(s).sort().join()!=='captions,youtubeTitle')throw Error('social requires youtubeTitle and captions');
 if(typeof s.youtubeTitle!=='string'||!s.youtubeTitle.trim()||s.youtubeTitle.length>100||/[<>]/.test(s.youtubeTitle))throw Error('YouTube title must be 1-100 characters without < or >');
 const c=s.captions;if(!c||typeof c!=='object'||Object.keys(c).sort().join()!=='instagram,tiktok,youtube')throw Error('social.captions requires instagram, tiktok and youtube');
 for(const [k,v]of Object.entries(c)){
  if(typeof v!=='string'||!v.trim()||v.length>2000)throw Error('Caption '+k+' must be 1-2000 characters');
  if(/https?:\/\/|www\./i.test(v))throw Error('Caption '+k+' must not contain links');
  if((v.match(/#[\p{L}\p{N}_]+/gu)??[]).length>30)throw Error('Caption '+k+' has more than 30 hashtags');
 }
 return s;
}
function tokens(l){return l.option===3?l.lessonData.opposites.map(pair=>'pair:'+pair.map(normalize).sort().join('|')):spokenContent(l).map(normalize);}
function duplicates(l,history){const used=new Map();for(const r of history.filter(r=>['published','publishing','publication_uncertain'].includes(r.status)))for(const text of r.content){const core=text.replace(/\s*\(r[eé]ponse\s*:.*?\)\s*$/i,'');const key=r.option===3?'pair:'+core.split(/\s*\/\s*|\.\s*/).filter(Boolean).map(normalize).sort().join('|'):normalize(core);used.set(key,r.id);}return tokens(l).filter(t=>used.has(t)).map(text=>({text,publication:used.get(text)}));}
function stableStringify(value){return value&&typeof value==='object'?Array.isArray(value)?'['+value.map(stableStringify).join(',')+']':'{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+stableStringify(value[k])).join(',')+'}':JSON.stringify(value);}
// Les légendes ne changent pas le rendu : les corriger n'invalide pas le MP4.
function fingerprint(l){const {social,...rendered}=l;return crypto.createHash('sha256').update(stableStringify(rendered)).digest('hex');}
module.exports={ROOT,read,total,validate,validateSocial,spokenContent,tokens,duplicates,normalize,fingerprint};
