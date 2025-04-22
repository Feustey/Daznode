# Tests Unitaires

Ce répertoire contient les tests unitaires pour les différentes composantes de l'application.

## Structure

```
tests/
├── api/                    # Tests des endpoints API
├── mocks/                  # Mocks des services externes
├── services/              # Tests des services
└── README.md              # Ce fichier
```

## Installation des dépendances

```bash
pip install -r requirements-dev.txt
```

## Exécution des tests

### Tous les tests

```bash
pytest
```

### Tests spécifiques

```bash
# Tests d'un module spécifique
pytest tests/services/

# Tests d'un fichier spécifique
pytest tests/services/test_data_sources.py

# Tests d'une classe spécifique
pytest tests/services/test_data_sources.py::TestLocalDataSource

# Tests d'une méthode spécifique
pytest tests/services/test_data_sources.py::TestLocalDataSource::test_get_node_info_success
```

### Options utiles

```bash
# Afficher les logs
pytest -v

# Afficher les print statements
pytest -s

# Exécuter uniquement les tests marqués comme lents
pytest -m slow

# Exécuter les tests en parallèle
pytest -n auto

# Générer un rapport de couverture
pytest --cov=services --cov-report=html
```

## Types de tests

### Tests unitaires

Les tests unitaires vérifient le comportement des composants individuels :

- `test_data_sources.py` : Tests des sources de données
- `test_health.py` : Tests de l'endpoint de health check

### Tests d'intégration

Les tests d'intégration vérifient l'interaction entre les composants :

- `test_api_integration.py` : Tests d'intégration de l'API

## Mocks

Les mocks sont utilisés pour simuler les services externes :

- `backend_clients.py` : Mocks des clients LND, MCP et LNRouter

## Bonnes pratiques

1. **Nommage des tests**
   - Les fichiers de test commencent par `test_`
   - Les classes de test commencent par `Test`
   - Les méthodes de test commencent par `test_`

2. **Organisation des tests**
   - Un test par assertion
   - Tests indépendants
   - Utilisation de fixtures pour la configuration

3. **Gestion des erreurs**
   - Tester les cas d'erreur
   - Vérifier les messages d'erreur
   - Tester les fallbacks

4. **Documentation**
   - Docstrings pour les classes et méthodes
   - Commentaires pour les parties complexes
   - README à jour 