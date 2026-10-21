const fs = require('node:fs');
const path = require('node:path');
const {ROOT, read} = require('./lesson.cjs');

function parisStamp(date = new Date()) {
  const parts = Object.fromEntries(new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Europe/Paris', year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23',
  }).formatToParts(date).map(p => [p.type, p.value]));
  return `${parts.year}-${parts.month}-${parts.day}_${parts.hour}-${parts.minute}-${parts.second}`;
}

function prepareVideo(option, {root = ROOT, now = new Date()} = {}) {
  if (!Number.isInteger(option) || option < 1 || option > 14) throw Error('Option must be 1..14');
  const fixture = read(path.join(root, `src/options/option-${option}/content.json`));
  const parent = path.join(root, `output/options/option-${option}`);
  fs.mkdirSync(parent, {recursive: true});
  fs.mkdirSync(path.join(root, 'content/episodes'), {recursive: true});
  const stamp = parisStamp(now);
  for (let attempt = 1; ; attempt++) {
    const folder = path.join(parent, stamp + (attempt === 1 ? '' : `-${String(attempt).padStart(2, '0')}`));
    const episode = path.join(root, 'content/episodes', `${path.basename(folder)}-option-${option}.json`);
    if (fs.existsSync(episode)) continue;
    try { fs.mkdirSync(folder); } catch (e) { if (e.code === 'EEXIST') continue; throw e; }
    // Exclusive creation prevents two requests from replacing the same episode.
    fs.writeFileSync(episode, JSON.stringify(fixture, null, 2) + '\n', {flag: 'wx'});
    const metadata = {
      option, status: 'draft', createdAt: now.toISOString(),
      createdAtParis: stamp.replace('_', ' ').replace(/(\d{2})-(\d{2})-(\d{2})$/, '$1:$2:$3'),
      timeZone: 'Europe/Paris', episode: path.relative(root, episode).replaceAll('\\', '/'),
      output: path.relative(root, folder).replaceAll('\\', '/'), video: `option-${option}.mp4`,
    };
    const manifest = path.join(folder, 'creation.json');
    fs.writeFileSync(manifest, JSON.stringify(metadata, null, 2) + '\n', {flag: 'wx'});
    return {manifest, episode, folder, metadata};
  }
}

module.exports = {parisStamp, prepareVideo};
