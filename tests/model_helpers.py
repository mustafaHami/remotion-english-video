"""Choix de modèle simulé pour les tests : aucun appel Codex ou Claude."""
QUOTAS = {engine: {'engine': engine, 'status': 'ok', 'exhausted': False, 'windows': [{'label': '5 h', 'remaining': 80}]}
          for engine in ('codex', 'claude')}


def select_model(app, store, engine='codex', quotas=None):
    identifier = app.model_menu(store)
    app.publish_model_menu(store, identifier, quotas or QUOTAS)
    app.select_model(store, identifier, engine)
    return identifier
