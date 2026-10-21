const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawnSync}=require('node:child_process');const {ROOT,read,validate,duplicates}=require('./lib/lesson.cjs');
const arg=k=>process.argv.find(a=>a.startsWith('--'+k+'='))?.split('=').slice(1).join('=');
const run=(cmd,args)=>{const p=spawnSync(cmd,args,{cwd:ROOT,encoding:'utf8',env:{...process.env,PYTHONUTF8:'1'},stdio:['ignore','pipe','pipe']});if(p.status!==0)throw Error(p.stderr||p.stdout||`Failed: ${cmd}`);return p.stdout};
const atomic=(file,data)=>{fs.mkdirSync(path.dirname(file),{recursive:true});const temp=file+'.tmp';fs.writeFileSync(temp,JSON.stringify(data,null,2)+'\n');fs.renameSync(temp,file)};
(async()=>{
 const date=arg('date');if(!/^\d{4}-\d{2}-\d{2}$/.test(date??'')||new Date(date).toISOString().slice(0,10)!==date)throw Error('Provide --date=YYYY-MM-DD explicitly (Europe/Paris).');
 const calendar=JSON.parse(run(process.env.PYTHON??'python',['scripts/planning/import-calendar.py']));const day=calendar.find(r=>r.date===date);
 if(!arg('content')){console.log(JSON.stringify({date,status:day&&Object.keys(day.options).length?'needs_content':'no_plan',brief:day?.options??{},next:'Agent prepares a new content JSON from the Excel brief, then runs with --content=PATH.'}));return;}
 const lesson=validate(read(path.resolve(arg('content'))));const n=lesson.option,id=`${date}-option-${n}`,historyPath=path.join(ROOT,'planning/publications.json'),history=read(historyPath);
 if(!day?.options[String(n)]||day.options[String(n)].startsWith('PUBLI'))throw Error('No unprocessed Excel brief for this date/option.');
 if(history.some(r=>r.id===id))throw Error('This date/option already has a publication record.');
 const repeated=duplicates(lesson,history);if(repeated.length)throw Error('Already published content: '+JSON.stringify(repeated));
 const fingerprint=require('./lib/lesson.cjs').fingerprint(lesson);
 if(process.argv.includes('--dry-run')){console.log(JSON.stringify({id,status:'ready_for_render',fingerprint}));return;}
 const dir=path.join(ROOT,'output/videos',id),statePath=path.join(ROOT,'.runtime/jobs',id+'.json'),lock=statePath+'.lock';fs.mkdirSync(path.dirname(lock),{recursive:true});let fd;
 try{fd=fs.openSync(lock,'wx');}catch{throw Error('Another process owns this job; inspect lock before retrying.');}
 try{
  let state=fs.existsSync(statePath)?read(statePath):{id,status:'new',fingerprint};
  if(state.fingerprint!==fingerprint)throw Error('Job content changed; review existing state before continuing.');
  if(['publishing','publication_uncertain','published'].includes(state.status))throw Error('Publication may already exist. Reconcile manually before retrying.');
  if(state.status!=='rendered'){
   state.status='rendering';atomic(statePath,state);
   run(process.execPath,['scripts/render.cjs','--content='+path.resolve(arg('content')),'--output='+dir]);
   run(process.env.PYTHON??'python',['scripts/verify-video.py','--folder='+dir]);state.status='rendered';atomic(statePath,state);
  }
  if(!process.argv.includes('--publish')){console.log(JSON.stringify({id,status:'rendered',video:path.join(dir,`option-${n}.mp4`)}));return;}
  if(process.env.PUBLISH_ENABLED!=='true'||!process.env.PUBLISHER_COMMAND)throw Error('Publishing not configured. Follow deploy/TODO-VPS.md.');
  const historyLock=historyPath+'.lock';let historyFd;
  try{historyFd=fs.openSync(historyLock,'wx');}catch{throw Error('Another publisher owns the history lock.');}
  try{
   const current=read(historyPath);if(duplicates(lesson,current).length||current.some(r=>r.id===id))throw Error('Content reserved or published while rendering.');
   const record={id,date,option:n,status:'publishing',content:require('./lib/lesson.cjs').spokenContent(lesson),platforms:[],publicationUrls:[],source:'Publisher in progress; do not retry blindly'};
   // Store pair identities in the same format as the historical publication records.
   if(n===3)record.content=lesson.lessonData.opposites.map(p=>p.join(' / '));
   current.push(record);atomic(historyPath,current);state.status='publishing';atomic(statePath,state);let receipt;
   try{receipt=JSON.parse(run(process.env.PUBLISHER_COMMAND,['--video='+path.join(dir,`option-${n}.mp4`),'--job='+id]));if(receipt.confirmed!==true||!Array.isArray(receipt.urls)||!receipt.urls.length||receipt.urls.some(u=>!/^https:\/\//.test(u)))throw Error('No confirmed publication receipt');}
   catch(e){state.status='publication_uncertain';record.status='publication_uncertain';atomic(statePath,state);atomic(historyPath,current);throw Error('Publication result uncertain; do not retry automatically. '+e.message);}
   state.status='published';state.receipt=receipt;atomic(statePath,state);
   record.status='published';record.platforms=receipt.platforms??[];record.publicationUrls=receipt.urls;record.source='Confirmed publisher receipt';atomic(historyPath,current);
   console.log(JSON.stringify({id,status:'published',urls:receipt.urls,next:'Synchronize Excel Journal and Calendrier from the confirmed receipt; never invent links.'}));
  }finally{fs.closeSync(historyFd);fs.unlinkSync(historyLock);}

 }finally{fs.closeSync(fd);fs.unlinkSync(lock);}
})().catch(e=>{console.error(e.message);process.exitCode=1});
