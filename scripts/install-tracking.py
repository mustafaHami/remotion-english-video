#!/usr/bin/env python3
"""Installe le suivi Excel et la rétention autorisée ; horaire Telegram explicite."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--daily-summary-time', choices=['09:00'], required=True)
p.add_argument('--start', action='store_true')
args = p.parse_args()
if os.geteuid() != 0:
    p.error('Exécuter avec sudo.')
os.umask(0o077)
if not (ROOT/'planning/production.json').exists():
    raise SystemExit('Synchroniser et vérifier le classeur avant activation.')
state = Path('/var/lib/englizy-tracking'); state.mkdir(mode=0o700, exist_ok=True); state.chmod(0o700)
configuration = {'database':'/var/lib/englizy-bridge/jobs.sqlite','mediaRoot':'/var/lib/englizy-media',
                 'stateDir':str(state),'retentionEnabled':True,
                 'policy':{'closedTaskDays':15,'sharedVideoDays':10,'openTasks':'explicit-request-only'}}
target = Path('/etc/englizy/tracking.json');target.write_text(json.dumps(configuration,indent=2)+'\n');target.chmod(0o600)
bridge_path = Path('/etc/englizy/bridge.json')
bridge = json.loads(bridge_path.read_text())
bridge.update(planningIndex='/srv/englizy-repository/planning/production.json',dailySummaryTime=args.daily_summary_time)
bridge_path.write_text(json.dumps(bridge,indent=2)+'\n')
for name in ['englizy-tracking.service','englizy-tracking.timer']:
    target=Path('/etc/systemd/system')/name
    shutil.copyfile(ROOT/'deploy/n8n'/name,target);target.chmod(0o644)
subprocess.run(['systemd-analyze','verify','/etc/systemd/system/englizy-tracking.service','/etc/systemd/system/englizy-tracking.timer'],check=True)
subprocess.run(['systemctl','daemon-reload'],check=True)
if args.start:
    subprocess.run(['systemctl','restart','englizy-bridge'],check=True)
    subprocess.run(['systemctl','start','englizy-tracking.service'],check=True)
    subprocess.run(['systemctl','enable','--now','englizy-tracking.timer'],check=True)
print(json.dumps({'trackingInstalled':True,'started':args.start,'dailySummaryTime':args.daily_summary_time,'timezone':'Europe/Paris'}))
