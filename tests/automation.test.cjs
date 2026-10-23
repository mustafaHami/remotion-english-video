const {test} = require('node:test');
const assert = require('node:assert/strict');
const {spawnSync} = require('node:child_process');

test('durable automation scenarios (simulated, no external calls)', () => {
  const result = spawnSync(process.env.PYTHON ?? (process.platform === 'win32' ? 'python' : 'python3'), ['-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_automation.py', '-v'], {encoding: 'utf8'});
  assert.equal(result.status, 0, result.stdout + result.stderr);
});
