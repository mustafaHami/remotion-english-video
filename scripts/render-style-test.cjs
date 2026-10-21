const path = require('path');
const fs = require('fs');
const {bundle} = require('@remotion/bundler');
const {openBrowser, selectComposition, renderStill, renderMedia} = require('@remotion/renderer');

(async () => {
  const variant = process.argv.find(arg=>arg.startsWith('--variant='))?.split('=')[1];
  const option = process.argv.find(arg=>arg.startsWith('--option='))?.split('=')[1];
  if(option && option!=='1') throw new Error('Seule l’option 1 est autorisée pour ce rendu.');
  const optionConfig=option==='1'?require('../src/archive/experiments/test-option-1/render-config.json'):null;
  const id = option==='1' ? 'TestOption1' : variant === 'tiktok' ? 'TestStyleV2-TikTok' : variant === 'instagram' ? 'TestStyleV2-Instagram' : 'TestStyleV1';
  const slug = option==='1' ? 'test-option-1' : variant ? `test-style-v2-${variant}` : 'test-style-v1';
  const out = path.resolve(`output/tests/${slug}`);
  const capturesDirectory=optionConfig?.capturesDirectory??'captures';
  fs.mkdirSync(path.join(out, capturesDirectory), {recursive:true});
  const serveUrl = await bundle({entryPoint:path.resolve('src/index.ts')});
  const browser = await openBrowser('chrome');
  const measurements = new Map();
  const onBrowserLog = ({text}) => {
    if (text.startsWith('STYLE_QA ')) {
      const record = JSON.parse(text.slice(9));
      measurements.set(record.frame,record);
    }
  };
  try {
    const composition = await selectComposition({serveUrl,id,puppeteerInstance:browser});
    const frames = optionConfig ? optionConfig.captures : variant ? [30,105,160,230,307,375,457,510,580,607,630,659] : [30,105,175,200,230,270,307,314,375,427,450,479];
    for (const frame of frames) {
      await renderStill({serveUrl,composition,puppeteerInstance:browser,onBrowserLog,frame,output:path.join(out,capturesDirectory,`frame-${String(frame).padStart(3,'0')}.png`)});
      console.log(`Capture ${frame}`);
    }
    if (!process.argv.includes('--stills-only')) {
      let last = -1;
      await renderMedia({serveUrl,composition,puppeteerInstance:browser,onBrowserLog,logLevel:'error',codec:'h264',colorSpace:'bt709',pixelFormat:'yuv420p',crf:18,concurrency:2,outputLocation:path.join(out,optionConfig?.filename??`${slug}.mp4`),
        onProgress:({progress})=>{const pct=Math.floor(progress*10)*10;if(pct!==last){last=pct;console.log(`Rendu ${pct}%`);}}});
      console.log('MP4 terminé : '+path.join(out,optionConfig?.filename??`${slug}.mp4`));
    }
    const records = [...measurements.values()].sort((a,b)=>a.frame-b.frame);
    const reportName=optionConfig?'layout-qa-v2':'layout-qa';
    fs.writeFileSync(path.join(out,`${reportName}${process.argv.includes('--stills-only')?'-stills':''}.json`),JSON.stringify(records,null,2));
    const failures = records.filter(record=>record.violations.length || record.fonts.some(ok=>!ok));
    console.log(`Mesures: ${records.length} frames, ${failures.length} erreurs`);
    if(failures.length) {console.error(failures);process.exitCode=1;}
  } finally {await browser.close({silent:true});}
})().catch(error=>{console.error(error);process.exitCode=1;});
