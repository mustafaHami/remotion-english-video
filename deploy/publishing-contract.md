# Adaptateur de publication

Le pipeline attend un exécutable configuré dans `PUBLISHER_COMMAND`, appelé sans shell :

```
<adaptateur> --video=<chemin-MP4> --job=<identifiant-stable>
```

L’adaptateur lit ses accès depuis l’environnement du VPS. Il valide le compte et la plateforme attendus, fournit l’identifiant de job comme clé d’idempotence quand la plateforme le permet, puis attend la confirmation réelle de publication. Il n’imprime jamais de secret.

Réponse JSON sur stdout après confirmation :

```json
{"confirmed":true,"platforms":["instagram"],"urls":["https://www.instagram.com/reel/IDENTIFIANT_REEL/"]}
```

Ce JSON illustre le schéma ; ce n’est pas un reçu réel. Un simple téléversement ou une mise en file ne vaut pas confirmation. Si une publication partielle, un timeout ou un résultat inconnu survient, retourner une erreur et réconcilier les publications déjà faites avant de relancer. Ne pas appeler plusieurs plateformes à l’aveugle après un échec partiel.

`PUBLISH_ENABLED=true` et `--publish` activent ce passage seulement quand l’adaptateur existe. Aucun adaptateur réseau ni identifiant de compte n’est inclus ici : ils seront configurés et documentés sur le VPS.
