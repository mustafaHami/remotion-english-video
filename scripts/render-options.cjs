const path=require('path');
const fs=require('fs');
const {bundle}=require('@remotion/bundler');
const {openBrowser,selectComposition,renderStill,renderMedia}=require('@remotion/renderer');
const revision=process.argv.includes('--revision=11')?11:process.argv.includes('--revision=10')?10:process.argv.includes('--revision=9')?9:process.argv.includes('--revision=8')?8:process.argv.includes('--revision=7')?7:process.argv.includes('--revision=6')?6:process.argv.includes('--revision=5')?5:process.argv.includes('--revision=4')?4:process.argv.includes('--revision=3')?3:2;
const config=revision>=3?require(`../src/archive/experiments/options-v${revision}/render-config.json`):require('../src/archive/experiments/options/render-config.json');
const baseLog=console.log;
console.log=(...args)=>{if(args.some(value=>typeof value==='string'&&value.includes('STYLE_QA ')))return;baseLog(...args);};
const selection=process.argv.find(arg=>arg.startsWith('--options='))?.split('=')[1]?.split(',').map(Number);
const keys=process.argv.find(arg=>arg.startsWith('--keys='))?.split('=')[1]?.split(',');
const options=config.filter(item=>(!selection||selection.includes(item.option))&&(!keys||keys.includes(item.key)));
if(!options.length)throw new Error('No matching test option');
const stillsOnly=process.argv.includes('--stills-only');
(async()=>{
  const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts')});
  const browser=await openBrowser('chrome',{logLevel:'error'});
  try{
    for(const item of options){
      const slug=`test-option-${item.option}`;
      const out=path.resolve('output/tests',slug);
      const suffix=revision>=3?`-v${revision}`+(item.key.includes('-')?'-'+item.verb:''):'';
      const capturesDirectory='captures'+suffix;
      fs.mkdirSync(path.join(out,capturesDirectory),{recursive:true});
      const records=new Map();
      const onBrowserLog=({text})=>{if(text.startsWith('STYLE_QA ')){const r=JSON.parse(text.slice(9));records.set(r.frame,r);}};
      const composition=await selectComposition({serveUrl,id:revision>=3?item.id:`TestOption${item.option}`,puppeteerInstance:browser});
      for(const frame of process.argv.includes('--skip-stills')?[]:item.captures){
        await renderStill({serveUrl,composition,puppeteerInstance:browser,onBrowserLog,logLevel:'error',frame,output:path.join(out,capturesDirectory,`frame-${String(frame).padStart(3,'0')}.png`)});
      }
      const preliminary=[...records.values()].filter(r=>r.violations.length||r.fonts.some(ok=>!ok));
      if(preliminary.length){fs.writeFileSync(path.join(out,`layout-qa${suffix}-stills.json`),JSON.stringify([...records.values()],null,2));throw new Error(`Option ${item.option}: capture errors ${JSON.stringify(preliminary)}`);}
      if(!stillsOnly){
        let last=-1;
        await renderMedia({serveUrl,composition,puppeteerInstance:browser,onBrowserLog,logLevel:'error',codec:'h264',colorSpace:'bt709',pixelFormat:'yuv420p',crf:18,concurrency:4,outputLocation:path.join(out,`${slug}${suffix}.mp4`),
          onProgress:({progress})=>{const pct=Math.floor(progress*4)*25;if(pct!==last){last=pct;console.log(`Option ${item.option}: ${pct}%`);}}});
      }
      const measured=[...records.values()].sort((a,b)=>a.frame-b.frame);
      fs.writeFileSync(path.join(out,`layout-qa${suffix}${stillsOnly?'-stills':''}.json`),JSON.stringify(measured,null,2));
      const failures=measured.filter(r=>r.violations.length||r.fonts.some(ok=>!ok));
      if(failures.length)throw new Error(`Option ${item.option}: ${JSON.stringify(failures.slice(0,5))}`);
      if(!stillsOnly&&measured.length!==item.frames)throw new Error(`Option ${item.option}: only ${measured.length}/${item.frames} frames measured`);
      console.log(`Option ${item.option}: ${measured.length} frames, zero layout errors; ${stillsOnly?'captures':'MP4'} ready.`);
    }
  }finally{await browser.close({silent:true});}
})().catch(e=>{console.error(e);process.exitCode=1;});
