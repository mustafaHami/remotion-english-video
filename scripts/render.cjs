const fs=require('node:fs'),path=require('node:path');
const {bundle}=require('@remotion/bundler');const {openBrowser,selectComposition,renderStill,renderMedia}=require('@remotion/renderer');
const {ROOT,read,validate,total}=require('./lib/lesson.cjs');
const arg=name=>process.argv.find(a=>a.startsWith('--'+name+'='))?.split('=').slice(1).join('=');
const all=process.argv.includes('--all'),stills=process.argv.includes('--stills-only');
const selection=arg('options')?.split(',').map(Number)??(arg('option')?[Number(arg('option'))]:null);
const lessons=arg('content')?[read(path.resolve(arg('content')))]:Array.from({length:14},(_,i)=>i+1).filter(n=>all||selection?.includes(n)).map(n=>read(path.join(ROOT,`src/options/option-${n}/content.json`)));
if(!lessons.length)throw Error('Use --all, --option=N or --content=PATH');
for(const l of lessons)validate(l);
const log=console.log;console.log=(...a)=>{if(!a.some(s=>typeof s==='string'&&s.includes('STYLE_QA ')))log(...a)};
(async()=>{const serveUrl=await bundle({entryPoint:path.join(ROOT,'src/index.ts')});const browser=await openBrowser('chrome',{logLevel:'error'});
try{for(const lesson of lessons){
 const n=lesson.option,t=lesson.timing,frames=total(lesson);
 const out=path.resolve(arg('output')??path.join(ROOT,`output/options/option-${n}`));if(!out.startsWith(path.join(ROOT,'output')+path.sep))throw Error('Output must remain inside output/');fs.mkdirSync(path.join(out,'captures'),{recursive:true});
 const composition=await selectComposition({serveUrl,id:`Option${n}`,inputProps:{lesson},puppeteerInstance:browser});
 const records=new Map(),onBrowserLog=({text})=>{if(text.startsWith('STYLE_QA ')){const r=JSON.parse(text.slice(9));records.set(r.frame,r);}};
 const captures=[Math.min(30,t.introFrames-1),t.introFrames+Math.min(100,t.bodyFrames-1),t.introFrames+Math.min(200,t.bodyFrames-1),t.introFrames+t.bodyFrames-30,t.introFrames+t.bodyFrames+23,frames-35];
 for(const frame of captures)await renderStill({serveUrl,composition,inputProps:{lesson},puppeteerInstance:browser,onBrowserLog,logLevel:'error',frame,output:path.join(out,'captures',`frame-${frame}.png`)});
 const fail=()=>[...records.values()].filter(r=>r.violations.length||r.fonts.some(ok=>!ok));if(fail().length)throw Error(JSON.stringify(fail().slice(0,3)));
 if(!stills){let last=-1;await renderMedia({serveUrl,composition,inputProps:{lesson},puppeteerInstance:browser,onBrowserLog,logLevel:'error',codec:'h264',colorSpace:'bt709',pixelFormat:'yuv420p',crf:18,concurrency:Number(process.env.RENDER_CONCURRENCY??4),outputLocation:path.join(out,`option-${n}.mp4`),onProgress:({progress})=>{const pct=Math.floor(progress*4)*25;if(pct!==last){last=pct;log(`Option ${n}: ${pct}%`)}}});}
 const qa=[...records.values()].sort((a,b)=>a.frame-b.frame);fs.writeFileSync(path.join(out,'layout-qa.json'),JSON.stringify(qa));fs.writeFileSync(path.join(out,'lesson.json'),JSON.stringify(lesson,null,2));fs.writeFileSync(path.join(out,'captures.json'),JSON.stringify(captures));
 if(fail().length||!stills&&qa.length!==frames)throw Error(`Option ${n}: failed layout/frame count`);log(`Option ${n}: ${stills?'stills':frames+' frames'}, no layout errors.`);
}}finally{await browser.close({silent:true})}})().catch(e=>{console.error(e);process.exitCode=1});
