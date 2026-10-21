const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {parisStamp, prepareVideo} = require('../scripts/lib/video-request.cjs');

test('request timestamps follow Paris winter/summer and the repeated DST hour', () => {
  assert.equal(parisStamp(new Date('2026-10-21T12:35:07Z')), '2026-10-21_14-35-07');
  assert.equal(parisStamp(new Date('2026-12-21T12:35:07Z')), '2026-12-21_13-35-07');
  assert.equal(parisStamp(new Date('2026-10-25T00:30:00Z')), parisStamp(new Date('2026-10-25T01:30:00Z')));
});

test('each request preserves previous work, even in the same second or repeated hour', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'remotion-request-'));
  try {
    const fixture = path.join(root, 'src/options/option-4');
    fs.mkdirSync(fixture, {recursive:true});
    fs.writeFileSync(path.join(fixture, 'content.json'), '{"option":4}');
    const first = prepareVideo(4, {root, now:new Date('2026-10-25T00:30:00Z')});
    fs.writeFileSync(first.episode, 'previous content');
    const second = prepareVideo(4, {root, now:new Date('2026-10-25T01:30:00Z')});
    assert.notEqual(first.folder, second.folder);
    assert.equal(path.basename(second.folder), '2026-10-25_02-30-00-02');
    assert.equal(fs.readFileSync(first.episode, 'utf8'), 'previous content');
    assert.equal(second.metadata.status, 'draft');
    assert.equal(second.metadata.createdAt, '2026-10-25T01:30:00.000Z');
    assert.equal(second.metadata.timeZone, 'Europe/Paris');
    assert.equal(fs.existsSync(path.join(second.folder, second.metadata.video)), false);
    assert.equal(fs.readFileSync(path.join(fixture, 'content.json'), 'utf8'), '{"option":4}');
    assert.throws(() => prepareVideo(15, {root}), /Option/);
  } finally { fs.rmSync(root, {recursive:true, force:true}); }
});
