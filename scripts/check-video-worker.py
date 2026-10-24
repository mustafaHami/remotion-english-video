#!/usr/bin/env python3
"""Préflight réel dans les montages du worker et le sandbox Codex, sans épisode ni vidéo."""
import argparse
import json
import os
import pwd
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--browser', action='store_true')
args = parser.parse_args()
if os.geteuid() != 0:
    parser.error('Exécuter avec sudo.')
user = pwd.getpwnam('englizy-worker')
pid = subprocess.check_output(['systemctl', 'show', '--value', '-pMainPID', 'englizy-worker'], text=True).strip()
if not pid.isdigit() or int(pid) <= 0:
    raise SystemExit('Worker non démarré.')
check = '''import os,json,uuid
from pathlib import Path
root=Path.cwd()
for name in ['AGENTS.md','.agents/skills/create-english-video/SKILL.md','planning/calendrier-publications.xlsx','planning/publications.json']:
 with (root/name).open('rb') as stream: assert stream.read(1)
for name in ['content/episodes','public/audio/production','output/options','node_modules/.cache']:
 file=root/name/('.access-check-'+uuid.uuid4().hex)
 with file.open('x') as stream: stream.write('temporary access test')
 file.unlink()
for name in ['src/options/option-1/content.json','planning/publications.json','.git/config','scripts/render.cjs']:
 try: fd=os.open(root/name,os.O_WRONLY)
 except OSError: continue
 else: os.close(fd);raise RuntimeError('Protected path unexpectedly writable: '+name)
assert not os.access('/var/lib/englizy/secrets/n8n-bridge-token',os.R_OK)
print(json.dumps({'sandboxReadAndTargetedWrite':True,'templatesHistoryGitReadOnly':True,'uid':os.getuid()}))
'''
command = ['codex', '-c', 'sandbox_mode="workspace-write"', '-c', 'sandbox_workspace_write.network_access=true', 'sandbox', '--',
           '/srv/englizy-repository/.venv/bin/python', '-c', check]
if args.browser:
    check += '''\nimport subprocess
subprocess.run(['node','-e',"require('@remotion/renderer').openBrowser('chrome',{logLevel:'error'}).then(async b=>{await b.close({silent:true});console.log('browser ready')}).catch(e=>{console.error(e.message);process.exit(1)})"],check=True)
'''
    command[-1] = check
launcher = 'import os,subprocess;os.chdir("/srv/englizy-repository");raise SystemExit(subprocess.run(' + repr(command) + ').returncode)'
result = subprocess.run(['nsenter', '--target', pid, '--mount', '--setuid', str(user.pw_uid), '--setgid', str(user.pw_gid),
                         '/usr/bin/env', '-i', 'HOME=' + user.pw_dir, 'CODEX_HOME=' + user.pw_dir + '/.codex',
                         'PATH=/usr/local/bin:/usr/bin:/bin', '/usr/bin/python3', '-c', launcher], timeout=90)
raise SystemExit(result.returncode)
