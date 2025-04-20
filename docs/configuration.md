# Configuration de Daznode

Ce document décrit les options de configuration disponibles pour Daznode.

## Variables d'environnement

La configuration de Daznode se fait principalement via des variables d'environnement, définies dans le fichier `.env`.

### Configuration générale

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `SECRET_KEY` | Clé secrète pour le chiffrement et les JWT | *Aucune (requis)* |
| `ENVIRONMENT` | Environnement d'exécution (`development`, `production`) | `development` |
| `DEBUG` | Active le mode debug | `false` |
| `LOG_LEVEL` | Niveau de logs (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` |

### Configuration du serveur API

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `SERVER_HOST` | Hôte du serveur | `0.0.0.0` |
| `SERVER_PORT` | Port du serveur | `8000` |
| `ROOT_PATH` | Chemin racine de l'API | `/` |
| `BACKEND_CORS_ORIGINS` | Origines autorisées pour CORS (format JSON) | `["http://localhost:3000"]` |

### Configuration LND

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `LND_HOST` | Hôte du nœud LND | `127.0.0.1` |
| `LND_PORT` | Port gRPC de LND | `10009` |
| `LND_CERT_PATH` | Chemin vers le certificat TLS | `/path/to/tls.cert` |
| `LND_MACAROON_PATH` | Chemin vers le macaroon admin | `/path/to/admin.macaroon` |
| `NODE_PUBKEY` | Clé publique de votre nœud | *Aucune (requis)* |

### Configuration de la base de données

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `DATABASE_URL` | URL de connexion à la base de données | `sqlite:///./daznode.db` |
| `DATABASE_POOL_SIZE` | Taille du pool de connexions | `5` |
| `DATABASE_MAX_OVERFLOW` | Nombre max de connexions additionnelles | `10` |

### Configuration MCP (Mempool Cloud Platform)

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `MCP_API_URL` | URL de l'API MCP | *Aucune (optionnel)* |
| `MCP_API_KEY` | Clé API pour MCP | *Aucune (optionnel)* |

### Configuration Feustey

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `FEUSTEY_API_URL` | URL de l'API Feustey | *Aucune (optionnel)* |
| `FEUSTEY_API_KEY` | Clé API pour Feustey | *Aucune (optionnel)* |

### Configuration de la sécurité

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée de validité des tokens JWT (minutes) | `60` |
| `RATE_LIMIT_PER_MINUTE` | Nombre max de requêtes par minute | `100` |
| `ENABLE_RATE_LIMIT` | Active le rate limiting | `true` |

## Fichier de configuration frontend

Le frontend utilise un fichier de configuration `.env.local` avec les variables suivantes :

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `NEXT_PUBLIC_API_URL` | URL de l'API backend | `http://localhost:8000` |
| `NEXT_PUBLIC_WEBSOCKET_URL` | URL du WebSocket | `ws://localhost:8000/ws` |
| `NEXT_PUBLIC_DEFAULT_LOCALE` | Locale par défaut | `fr` |
| `NEXT_PUBLIC_ALBY_ENABLED` | Active l'intégration Alby | `false` |
| `ALBY_WEBHOOK_SECRET` | Secret pour les webhooks Alby | *Aucune (optionnel)* |

## Configuration Docker

Si vous utilisez Docker, les variables d'environnement peuvent être définies dans le fichier `docker-compose.yml` :

```yaml
version: '3'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - SECRET_KEY=your-secret-key
      - ENVIRONMENT=production
      - LND_HOST=lightning
      - LND_PORT=10009
      - LND_CERT_PATH=/etc/lnd/tls.cert
      - LND_MACAROON_PATH=/etc/lnd/admin.macaroon
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/daznode
    volumes:
      - ./data/lnd:/etc/lnd:ro
    ports:
      - "8000:8000"
    depends_on:
      - db

  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=daznode
    volumes:
      - postgres_data:/var/lib/postgresql/data

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - api

volumes:
  postgres_data:
```

## Configuration Umbrel

Sur Umbrel, la configuration se fait via le fichier `umbrel-app.yml` :

```yaml
manifestVersion: 1
id: daznode
name: Daznode
tagline: Monitoring performant pour votre nœud Lightning
icon: https://i.imgur.com/your-icon.png
category: Lightning
version: "0.1.0"
port: 8000
description: >-
  Daznode est une application de monitoring pour les nœuds Lightning Network.
  Elle permet de suivre les performances d'un nœud, d'analyser le réseau et d'optimiser la gestion des canaux.
developer: Equipe Daznode
website: https://github.com/yourusername/daznode
dependencies:
  - lightning
repo: https://github.com/yourusername/daznode
support: https://github.com/yourusername/daznode/issues
permissions:
  - lnd
  - bitcoind
```

## Configuration avancée

### Tâches planifiées

Daznode peut exécuter des tâches planifiées pour la collecte de données régulière. Configurez-les dans le fichier `scheduler.py` :

```python
SCHEDULER_JOBS = [
    {
        "id": "daily_metrics_snapshot",
        "func": "services.metrics_collector:create_daily_snapshot",
        "trigger": "cron",
        "hour": 0,
        "minute": 0
    },
    {
        "id": "network_graph_refresh",
        "func": "services.lnrouter_client:refresh_graph",
        "trigger": "interval",
        "hours": 6
    }
]
```

### Logging

La configuration des logs peut être personnalisée dans le fichier `logging.conf` :

```ini
[loggers]
keys=root,daznode

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_daznode]
level=INFO
handlers=consoleHandler,fileHandler
qualname=daznode
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=logging.handlers.RotatingFileHandler
level=INFO
formatter=simpleFormatter
args=('logs/daznode.log', 'a', 10485760, 5)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
datefmt=%Y-%m-%d %H:%M:%S
``` 