#!/usr/bin/env python3
"""Saisie locale sans écho ; aucun secret dans les arguments ou le dépôt."""
import argparse
import getpass
import os
from pathlib import Path
import tempfile
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('name', choices=['n8n-api-key', 'github-pat', 'buffer-access-token'])
args = parser.parse_args()
if os.geteuid() != 0:
    parser.error('Exécuter avec sudo, dans le terminal SSH du VPS.')
if not sys.stdin.isatty():
    parser.error('Un terminal interactif est requis pour garantir la saisie masquée.')
directory = Path('/var/lib/englizy/secrets')
directory.mkdir(mode=0o700, parents=True, exist_ok=True)
directory.chmod(0o700)
value = getpass.getpass(f'{args.name} (saisie masquée) : ').strip()
if not value or any(c.isspace() for c in value):
    parser.error('Valeur vide ou contenant des espaces refusée.')
fd, temporary = tempfile.mkstemp(dir=directory)
try:
    with os.fdopen(fd, 'w') as stream:
        stream.write(value)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, directory / args.name)
finally:
    if os.path.exists(temporary):
        os.unlink(temporary)
print(f'Secret enregistré dans {directory / args.name} (0600).')
