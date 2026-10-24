#!/usr/bin/env python3
"""GitHub CLI et helper Git : PAT protégé, jamais dans les arguments/configurations."""
import os
from pathlib import Path
import subprocess
import sys

SECRET = Path('/var/lib/englizy/secrets/github-pat')
REPOSITORY = Path('/root/projects/remotion-english-video')


def token():
    if SECRET.is_symlink() or SECRET.stat().st_mode & 0o077:
        raise RuntimeError('Le PAT doit être un fichier privé 0600, sans lien symbolique.')
    value = SECRET.read_text().strip()
    if not value or any(c.isspace() for c in value):
        raise RuntimeError('PAT absent ou invalide.')
    return value


def helper(operation):
    # Git consomme cette sortie directement ; ne jamais appeler le helper pour l'afficher.
    if operation != 'get':
        return
    fields = dict(line.rstrip('\n').split('=', 1) for line in sys.stdin if '=' in line)
    if (fields.get('protocol') != 'https' or fields.get('host') != 'github.com'
            or fields.get('path') not in ['mustafaHami/remotion-english-video', 'mustafaHami/remotion-english-video.git']):
        return
    sys.stdout.write('username=x-access-token\npassword=' + token() + '\n\n')


def main():
    args = sys.argv[1:]
    if args and args[0] == 'credential-helper':
        helper(args[1] if len(args) > 1 else '')
        return
    if args == ['configure-git']:
        token()  # Vérifier l'existence avant de modifier la configuration locale.
        script = str(Path(__file__).resolve())
        scope = 'credential.https://github.com/mustafaHami/remotion-english-video.git.helper'
        subprocess.run(['git', '-C', str(REPOSITORY), 'config', '--local', 'credential.useHttpPath', 'true'], check=True)
        # Une valeur vide annule les éventuels helpers globaux pour ce seul dépôt distant.
        subprocess.run(['git', '-C', str(REPOSITORY), 'config', '--local', '--replace-all', scope, ''], check=True)
        subprocess.run(['git', '-C', str(REPOSITORY), 'config', '--local', '--add', scope,
                        '!/usr/bin/python3 ' + script + ' credential-helper'], check=True)
        print('Helper Git configuré uniquement pour le dépôt personnel. Aucun jeton dans .git/config.')
        return
    if args and args[0] == 'gh':
        if args[1:3] == ['auth', 'token'] or '--show-token' in args:
            raise RuntimeError('Affichage du jeton désactivé dans ce lanceur.')
        env = {**os.environ, 'GH_TOKEN': token(), 'GH_HOST': 'github.com'}
        env.pop('GH_DEBUG', None)
        raise SystemExit(subprocess.run(['gh', *args[1:]], env=env).returncode)
    raise RuntimeError('Utiliser configure-git ou gh <arguments>.')


if __name__ == '__main__':
    try:
        main()
    except (FileNotFoundError, RuntimeError) as error:
        raise SystemExit('PAT local manquant.' if isinstance(error, FileNotFoundError) else str(error)) from None
