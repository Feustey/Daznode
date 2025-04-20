# Documentation de l'API Daznode

L'API REST de Daznode permet d'interagir avec votre nœud Lightning Network et d'accéder aux données de monitoring.

## Base URL

```
http://<votre-serveur>:8000/api/v1
```

## Authentification

L'API utilise une authentification par token JWT. Pour obtenir un token, utilisez l'endpoint d'authentification.

## Endpoints

### Nœud

#### Obtenir les informations du nœud

```
GET /node/info
```

Retourne les informations de base sur votre nœud Lightning Network.

**Exemple de réponse :**
```json
{
  "alias": "Feustey",
  "pubkey": "02778f4a4eb3a2344b9fd8ee72e7ec5f03f803e5f5273e2e1a2af508",
  "block_height": 820305,
  "synced_to_chain": true,
  "num_active_channels": 12
}
```

#### Obtenir les métriques du nœud

```
GET /node/metrics
```

Retourne les métriques détaillées de votre nœud.

### Canaux

#### Lister les canaux

```
GET /channels
```

**Paramètres :**
- `active` (optionnel) - Filtrer les canaux actifs (true/false)

Retourne la liste des canaux du nœud.

#### Obtenir les métriques des canaux

```
GET /channels/metrics
```

Retourne les métriques détaillées des canaux.

#### Obtenir les performances des canaux

```
GET /channels/performance
```

**Paramètres :**
- `days` (optionnel, défaut: 30) - Nombre de jours d'historique

Retourne les données de performance des canaux.

### Forwarding

#### Obtenir l'historique de forwarding

```
GET /forwarding
```

**Paramètres :**
- `hours` (optionnel, défaut: 24) - Nombre d'heures d'historique
- `limit` (optionnel, défaut: 1000) - Limite de résultats

Retourne l'historique des opérations de forwarding.

#### Obtenir les métriques de forwarding

```
GET /forwarding/metrics
```

**Paramètres :**
- `hours` (optionnel, défaut: 24) - Nombre d'heures d'historique

Retourne les métriques agrégées de forwarding.

#### Obtenir la heatmap de forwarding

```
GET /forwarding/heatmap
```

**Paramètres :**
- `resolution` (optionnel, défaut: "hour") - Résolution temporelle (hour, day, week)

Retourne les données pour une heatmap de routage.

### Optimisation

#### Obtenir les suggestions d'optimisation de frais

```
GET /optimization/fees
```

Retourne des suggestions d'optimisation des frais pour vos canaux.

### Réseau

#### Obtenir le graphe du réseau

```
GET /network/graph
```

Retourne les données pour un graphe du réseau local.

#### Obtenir les statistiques du réseau

```
GET /network/stats
```

Retourne les statistiques globales du réseau Lightning.

#### Obtenir les détails d'un nœud spécifique

```
GET /network/node/{pubkey}
```

**Paramètres :**
- `pubkey` - Clé publique du nœud

Retourne les détails d'un nœud spécifique.

### Métriques

#### Créer un snapshot quotidien

```
POST /metrics/snapshot
```

Crée un snapshot quotidien des métriques.

### Rapports

#### Générer un rapport

```
GET /reports/{report_type}
```

**Paramètres :**
- `report_type` - Type de rapport (daily, weekly, monthly)
- `parameters` (optionnel) - Paramètres du rapport

Génère un rapport périodique.

### Système

#### Vérifier l'état de l'API

```
GET /health
```

Vérifie l'état de l'API.

#### Obtenir l'état du nœud

```
GET /status
```

Retourne l'état du nœud et des services associés.

## Codes de statut

- `200` - Succès
- `400` - Requête invalide
- `401` - Non authentifié
- `403` - Non autorisé
- `404` - Ressource non trouvée
- `500` - Erreur serveur 