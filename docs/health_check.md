# Système de Health Check

## Vue d'ensemble

Le système de health check surveille continuellement la disponibilité des différentes sources de données (LND, MCP, LNRouter) et permet une sélection intelligente de la source à utiliser.

## Fonctionnalités

- Vérification périodique de l'état des sources
- Détection automatique des défaillances
- Sélection intelligente de la source de données
- Exposition de l'état via l'API
- Persistance des données entre les redémarrages

## Configuration

Les paramètres de configuration sont disponibles dans le fichier `.env` :

```env
# Intervalle entre les vérifications (en secondes)
HEALTH_CHECK_INTERVAL=60

# Nombre d'échecs avant de considérer une source comme inactive
HEALTH_CHECK_FAILURE_THRESHOLD=3

# Source de données par défaut (local, mcp, auto)
DEFAULT_DATA_SOURCE=auto
```

## API

### GET /api/v1/system/health

Retourne l'état de santé des sources de données :

```json
{
  "timestamp": "2024-03-21T10:00:00Z",
  "sources": {
    "lnd": {
      "status": "ok",
      "last_check": "2024-03-21T10:00:00Z",
      "error": null,
      "details": {
        "alias": "my_node",
        "pubkey": "abc123",
        "block_height": 700000,
        "synced": true,
        "response_time_ms": 45.2
      }
    },
    "mcp": {
      "status": "ok",
      "last_check": "2024-03-21T10:00:00Z",
      "error": null,
      "details": {
        "api_url": "https://api.mcp.test",
        "has_api_key": true,
        "network_stats": {
          "nodes_count": 10000,
          "channels_count": 50000
        },
        "response_time_ms": 120.5
      }
    },
    "lnrouter": {
      "status": "ok",
      "last_check": "2024-03-21T10:00:00Z",
      "error": null,
      "details": {
        "api_url": "https://lnrouter.test/api",
        "has_api_key": true,
        "cache_status": "valid",
        "cache_details": {
          "nodes_count": 1000,
          "channels_count": 5000,
          "cache_age_hours": 2.5,
          "last_update": "2024-03-21T07:30:00Z"
        }
      }
    }
  },
  "global_status": "ok"
}
```

## États possibles

- `ok` : La source est fonctionnelle
- `degraded` : La source présente des problèmes mais est encore utilisable
- `error` : La source est complètement indisponible
- `unavailable` : La source n'est pas configurée
- `unknown` : État indéterminé

## Stratégie de fallback

En mode `auto`, la sélection de la source se fait selon l'ordre de priorité suivant :

1. MCP (si configuré et disponible)
2. Local (si disponible)
3. Cache local (en dernier recours)

## Dépannage

### Problèmes courants

1. **Source LND indisponible**
   - Vérifier la connexion au nœud LND
   - Vérifier les permissions du macaroon
   - Vérifier le certificat TLS

2. **Source MCP indisponible**
   - Vérifier la clé API
   - Vérifier la connexion Internet
   - Vérifier le taux limite d'API

3. **Source LNRouter indisponible**
   - Vérifier la clé API
   - Vérifier l'état du cache
   - Vérifier la connexion Internet

### Logs

Les erreurs et les changements d'état sont enregistrés dans les logs avec les niveaux suivants :
- INFO : Changements d'état normaux
- WARNING : Problèmes temporaires
- ERROR : Échecs critiques

## Tests

Le système inclut une suite complète de tests unitaires couvrant :
- La vérification d'état des sources
- La gestion des erreurs
- La sélection automatique des sources
- L'API de health check 