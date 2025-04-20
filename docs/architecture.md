# Architecture de Daznode

Ce document décrit l'architecture globale de l'application Daznode.

## Vue d'ensemble

Daznode est conçu selon une architecture modulaire avec une séparation claire entre le backend et le frontend. L'application s'intègre avec différentes implémentations de nœuds Lightning et offre des fonctionnalités avancées d'analyse et de visualisation.

```
+-------------------+     +-------------------+     +-------------------+
|                   |     |                   |     |                   |
|  Node Lightning   |<--->|  Backend Daznode  |<--->|  Frontend Daznode |
|  (LND, c-light.)  |     |  (API FastAPI)    |     |  (Next.js)        |
|                   |     |                   |     |                   |
+-------------------+     +-------------------+     +-------------------+
                               ^       ^
                               |       |
                               v       v
                    +------------------+  +------------------+
                    |                  |  |                  |
                    | Services externes|  |     Base de      |
                    | (LNRouter, MCP)  |  |     données      |
                    |                  |  |                  |
                    +------------------+  +------------------+
```

## Composants principaux

### Backend

Le backend de Daznode est construit autour d'une API REST développée avec FastAPI.

#### Services

- **LNDClient** - Interface avec le nœud LND
- **LNRouterClient** - Interface avec l'API LNRouter pour les données réseau
- **MetricsCollector** - Collecte et traite les métriques du nœud
- **NodeAggregator** - Agrège les informations sur les nœuds du réseau
- **VisualizationExporter** - Génère des datasets pour visualisation
- **FeusteyService** - Service d'accès à l'API Feustey

#### API Endpoints

L'API est organisée en différents groupes d'endpoints :
- `/api/v1/node/` - Endpoints relatifs au nœud local
- `/api/v1/channels/` - Endpoints de gestion des canaux
- `/api/v1/forwarding/` - Endpoints liés au forwarding
- `/api/v1/network/` - Endpoints d'analyse du réseau
- `/api/v1/metrics/` - Endpoints de métriques
- `/api/v1/reports/` - Endpoints de génération de rapports

### Frontend

Le frontend de Daznode est développé avec Next.js et Tailwind CSS.

#### Structure

```
frontend/
├── src/
│   ├── app/                 # Routage Next.js
│   │   ├── [locale]/        # Routes localisées
│   │   ├── api/             # Routes API
│   ├── components/          # Composants React
│   │   ├── layout/          # Composants de mise en page
│   │   ├── ui/              # Composants d'interface
│   ├── lib/                 # Utilitaires et modèles
│   │   ├── contexts/        # Contextes React
│   │   ├── types/           # Types TypeScript
│   │   ├── utils/           # Fonctions utilitaires
│   │   └── websocket/       # Gestion WebSocket
│   ├── styles/              # Styles CSS
```

#### Composants clés

- **NodeDashboard** - Tableau de bord principal du nœud
- **ChannelsTable** - Tableau des canaux avec métriques
- **NetworkGraph** - Visualisation du graphe du réseau
- **StatsGrid** - Grille de statistiques principales

## Flux de données

1. **Collecte des données** : Les services `LNDClient` et `LNRouterClient` collectent les données brutes
2. **Traitement des données** : `MetricsCollector` et `NodeAggregator` traitent et enrichissent les données
3. **Préparation des visualisations** : `VisualizationExporter` génère les datasets pour les visualisations
4. **Exposition via API** : Les endpoints FastAPI exposent les données
5. **Consommation par le frontend** : Le frontend Next.js consomme l'API et affiche les données
6. **Mises à jour en temps réel** : WebSocket pour les mises à jour dynamiques

## Intégrations

### Nœuds Lightning

Daznode s'intègre avec différentes implémentations de nœuds Lightning :
- **LND** - Principal nœud supporté
- **c-lightning** - Support partiel
- **Eclair** - Support prévu

### Services externes

- **LNRouter** - Données sur le réseau Lightning global
- **MCP (Mempool Cloud Platform)** - Données contextuelles réseau
- **Alby Wallet** - Intégration pour les paiements Lightning

## Stockage des données

Daznode utilise une combinaison de :
- **Base de données PostgreSQL** - Pour les données persistantes
- **Cache en mémoire** - Pour les données fréquemment accédées
- **Snapshots quotidiens** - Pour l'analyse historique des performances

## Sécurité

- **Authentification JWT** - Pour l'accès à l'API
- **Protection contre les attaques** - Rate limiting, validation des entrées
- **Headers de sécurité** - Configuration robuste des en-têtes HTTP
- **Sessions sécurisées** - Avec expiration et rotation des tokens 