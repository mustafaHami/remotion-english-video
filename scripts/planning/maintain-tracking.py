#!/usr/bin/env python3
"""Synchronise le suivi et applique la rétention configurée, sous verrou exclusif."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from automation import planning, retention
from automation.store import Store


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', required=True, type=Path)
    args = p.parse_args()
    os.umask(0o077)
    config = json.loads(args.config.read_text())
    state = Path(config['stateDir']); state.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (state/'maintenance.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        result = planning.sync(config['database'], ROOT, state/'workbooks')
        if config.get('retentionEnabled'):
            store = Store(config['database'], owner_permissions=True)
            try:
                result['retention'] = retention.apply(store, ROOT, config['mediaRoot'], state/'database-backups')
            finally:
                store.close()
        (state/'latest.json').write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(result))


if __name__ == '__main__':
    main()
