const fs = require('node:fs');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const {ROOT, read, validate, duplicates, fingerprint} = require('./lib/lesson.cjs');
const {prepareVideo} = require('./lib/video-request.cjs');
const arg = key => process.argv.find(a => a.startsWith(`--${key}=`))?.slice(key.length + 3);
const run = (command, args) => {
  const result = spawnSync(command, args, {cwd: ROOT, stdio: 'inherit', env: {...process.env, PYTHONUTF8: '1'}});
  if (result.error) throw result.error;
  if (result.status !== 0) throw Error(`${command} failed (${result.status})`);
};
function renderRequest(manifest) {
  const file = path.resolve(manifest), data = read(file);
  const folder = path.resolve(ROOT, data.output), episode = path.resolve(ROOT, data.episode);
  const parent = path.join(ROOT, `output/options/option-${data.option}`);
  if (!Number.isInteger(data.option) || data.option < 1 || data.option > 14 ||
      path.dirname(folder) !== parent || file !== path.join(folder, 'creation.json') ||
      path.dirname(episode) !== path.join(ROOT, 'content/episodes') || data.video !== `option-${data.option}.mp4`) {
    throw Error('Invalid creation manifest or paths');
  }
  const lock = file + '.lock';
  const fd = fs.openSync(lock, 'wx');
  const save = () => fs.writeFileSync(file, JSON.stringify(data, null, 2) + '\n');
  try {
    if (fs.existsSync(path.join(folder, data.video)) || data.status === 'verified') {
      throw Error('This request already has a video. Prepare a new request to preserve it.');
    }
    let lesson = read(episode);
    if (lesson.option !== data.option) throw Error('Episode option differs from request');
    validate(lesson, {assets: false});
    const repeated = duplicates(lesson, read(path.join(ROOT, 'planning/publications.json')));
    if (repeated.length) throw Error('Already published content: ' + JSON.stringify(repeated));
    delete data.error; data.status = 'preparing'; save();
    const localPython = path.join(ROOT, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
    const python = process.env.PYTHON ?? (fs.existsSync(localPython) ? localPython : 'python');
    run(python, ['scripts/prepare-audio.py', '--content', episode]);
    if (data.option === 1) run(python, ['scripts/build-writing-paths.py', '--content', episode]);
    lesson = validate(read(episode));
    data.contentFingerprint = fingerprint(lesson); data.status = 'rendering'; save();
    run(process.execPath, ['scripts/render.cjs', '--content=' + episode, '--output=' + folder]);
    data.renderedAt = new Date().toISOString(); data.status = 'rendered'; save();
    run(python, ['scripts/verify-video.py', '--folder', folder]);
    data.verifiedAt = new Date().toISOString(); data.status = 'verified'; save();
    console.log(JSON.stringify({video: path.join(folder, data.video), manifest: file, status: data.status}, null, 2));
  } catch (e) {
    // Do not change a finished request on an accidental second invocation.
    if (!['draft', 'verified'].includes(data.status)) { data.status = 'failed'; data.error = e.message; save(); }
    throw e;
  } finally { fs.closeSync(fd); fs.unlinkSync(lock); }
}
try {
  if (arg('render')) renderRequest(arg('render'));
  else if (arg('option')) console.log(JSON.stringify(prepareVideo(Number(arg('option'))), null, 2));
  else throw Error('Use --option=N to prepare, or --render=PATH/creation.json after editing the episode.');
} catch (e) { console.error(e.message); process.exitCode = 1; }
