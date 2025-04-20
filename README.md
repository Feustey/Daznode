# Daznode - Application de monitoring pour nœuds Lightning

Daznode est une application de monitoring pour les nœuds Lightning Network, écrite en Python avec FastAPI.
Elle permet de suivre les performances d'un nœud, analyser le réseau et optimiser la gestion des canaux.

## Fonctionnalités

- **Tableau de bord** : Vue d'ensemble des performances de votre nœud
- **Analyses du réseau** : Statistiques et visualisations du réseau Lightning
- **Gestion des canaux** : Suivi et optimisation de vos canaux Lightning
- **Intégration avec MCP** : Données contextuelles du réseau grâce à l'API MCP
- **Compatible Umbrel** : Installation facile sur votre Umbrel

## Prérequis

- Python 3.9+
- Nœud Lightning (LND, c-lightning, etc.)
- Accès à l'API MCP (optionnel mais recommandé)

## Installation

### Configuration de l'environnement

1. Cloner le dépôt :

   ```bash
   git clone https://github.com/yourusername/daznode.git
   cd daznode
   ```

2. Créer un environnement virtuel et l'activer :

   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

3. Installer les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

4. Configurer les variables d'environnement :
   ```bash
   cp .env.example .env
   # Éditez le fichier .env avec vos propres configurations
   ```

### Lancement de l'application

```bash
uvicorn main:app --reload
```

L'application sera accessible à l'adresse : http://localhost:8000

L'API est documentée à l'adresse : http://localhost:8000/api/v1/docs

## Structure du projet

```
daznode/
├── app/
│   ├── api/
│   │   ├── api_v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py
│   │   │   │   ├── channels.py
│   │   │   │   ├── dashboard.py
│   │   │   │   └── network.py
│   │   │   └── api.py
│   │   └── deps.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── crud/
│   │   └── user.py
│   ├── db/
│   │   └── session.py
│   ├── models/
│   │   └── user.py
│   ├── schemas/
│   │   ├── channel.py
│   │   ├── dashboard.py
│   │   ├── network.py
│   │   ├── token.py
│   │   └── user.py
│   └── services/
│       ├── feustey.py
│       └── mcp.py
├── static/
├── templates/
├── .env
├── .env.example
├── main.py
└── requirements.txt
```

## Utilisation

### API

L'API REST est accessible via le préfixe `/api/v1` et propose les endpoints suivants :

- **Authentification** : `/api/v1/auth/`
- **Réseau** : `/api/v1/network/`
- **Canaux** : `/api/v1/channels/`
- **Tableau de bord** : `/api/v1/dashboard/`

Consultez la documentation interactive pour plus de détails : `/api/v1/docs`

### Interface utilisateur

_Note : Cette version est axée sur l'API. Une interface utilisateur complète sera développée dans une version future._

## Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

---

Fait avec ⚡️ par l'équipe Daznode

# Daznode 🌩️

Daznode est un tableau de bord intelligent propulsé par l'IA, conçu pour optimiser votre nœud Lightning Network et maximiser sa rentabilité.

## 🚀 Caractéristiques

- **Analyse en Temps Réel** : Surveillez les performances de votre nœud avec des métriques mises à jour en direct
- **Visualisation des Données** : Graphiques interactifs pour suivre :
  - Revenus et volumes de transactions
  - Croissance des canaux
  - Capacité du réseau
  - Évolution du nombre de pairs
- **Statistiques Détaillées** :
  - Revenus totaux et taux de frais moyens
  - Capacité des canaux et nombre de canaux actifs
  - Volume total des transactions
  - Statistiques réseau et temps de fonctionnement
- **Recommandations Intelligentes** : Conseils basés sur l'analyse des données pour optimiser votre nœud
- **Bot IA Premium** :
  - Recommandations personnalisées en one-shot (10,000 sats)
  - Abonnement annuel avec accès complet (100,000 sats)
  - Intégration Nostr Wallet Connect (NWC) avec Alby
  - Mode développement avec simulation de paiement
- **Sécurité Renforcée** :
  - Protection contre les attaques par force brute
  - Rate limiting intelligent par route
  - Sessions sécurisées avec expiration
  - Validation stricte des entrées
  - Headers de sécurité configurés
  - Protection CSRF et XSS

## 🛠️ Technologies Utilisées

- **Frontend** : Next.js 14.2
- **UI/UX** : Tailwind CSS
- **Graphiques** : Chart.js avec react-chartjs-2
- **État** : React Hooks
- **Types** : TypeScript
- **API** : API MCP pour les données Lightning Network
- **Base de données** : PostgreSQL
- **i18n** : next-intl pour l'internationalisation
- **Paiements** :
  - Intégration Nostr Wallet Connect (NWC)
  - Support Alby Wallet
  - Paiements Lightning Network natifs
- **Animations** : Framer Motion pour les interactions
- **Sécurité** :
  - Rate limiting personnalisé
  - Sessions sécurisées
  - Validation des données
  - Protection contre les attaques

## 📦 Installation

1. Cloner le dépôt :

```bash
git clone https://github.com/votre-username/Daznode.git
cd Daznode
```

2. Installer les dépendances :

```bash
npm install
# ou
yarn install
```

3. Lancer le serveur de développement :

```bash
npm run dev
# ou
yarn dev
```

4. Ouvrir [http://localhost:3000](http://localhost:3000) dans votre navigateur

## 🔧 Configuration

1. Créez un fichier `.env.local` à la racine du projet
2. Ajoutez vos variables d'environnement :

```env
# Configuration PostgreSQL
DATABASE_URL="votre_url_postgresql"
DIRECT_URL="votre_url_direct_postgresql"

# Configuration MCP
MCP_API_URL="https://daznode-mcp.herokuapp.com"
NODE_PUBKEY="votre_clé_publique"

# Configuration Alby
ALBY_WEBHOOK_SECRET="votre_secret_webhook"

# Configuration JWT
JWT_SECRET="votre_secret_jwt"

# Configuration SMTP
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="votre_email@gmail.com"
SMTP_PASS="votre_mot_de_passe_app"
SMTP_FROM="Daznode <votre_email@gmail.com>"
```

## 📊 Architecture

### Structure du projet

```
app/
├── [locale]/        # Routes localisées (fr, en)
│   ├── @app/        # Routes parallèles
│   ├── bot-ia/      # Page de tarification du bot IA
├── api/             # Routes API
├── components/      # Composants React
├── config/          # Configuration
├── contexts/        # Contextes React
├── lib/             # Utilitaires et modèles
├── middleware/      # Middlewares (rate limiting, etc.)
├── styles/          # Styles globaux
└── types/           # Types TypeScript
```

### Sécurité

- **Rate Limiting** :

  - Limite de 100 requêtes par 15 minutes par IP
  - Limite de 5 tentatives par 15 minutes pour la vérification
  - Nettoyage automatique des anciennes entrées

- **Sessions** :

  - Durée de vie de 24 heures
  - Cookies sécurisés (httpOnly, secure, sameSite)
  - Expiration automatique
  - Régénération des identifiants

- **Validation** :

  - Validation stricte des entrées
  - Protection contre les injections
  - Sanitization des données

- **Headers de Sécurité** :
  - CSP configuré
  - HSTS activé
  - Protection XSS et CSRF
  - Politique de permissions restrictive

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'feat: Ajout d'une fonctionnalité'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

Fait avec ⚡️ par l'équipe Daznode

# Daznode - Gestionnaire de nœud Lightning Network

Daznode est un ensemble d'outils pour gérer, surveiller et analyser un nœud Lightning Network.

## Fonctionnalités

- **Surveillance de nœud** : Visualisation de l'état du nœud, des canaux et de la liquidité
- **Analyse de performance** : Suivi des forwards, des frais et de la rentabilité
- **Optimisation** : Suggestions pour l'équilibrage des canaux et l'ajustement des frais
- **Visualisation** : Exportation de données pour tableaux de bord et graphiques
- **Interface CLI** : Interaction simple via la ligne de commande
- **API REST** : Exposez les fonctionnalités via une API web

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/yourusername/daznode.git
cd daznode
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurer les accès à votre nœud LND dans le fichier `.env` :
```
LND_GRPC_HOST=localhost:10009
LND_TLS_CERT_PATH=/path/to/tls.cert
LND_MACAROON_PATH=/path/to/admin.macaroon
```

## Utilisation du CLI

Daznode fournit une interface en ligne de commande complète pour interagir avec votre nœud.

### Informations de base

```bash
# Afficher les informations du nœud
./daznode-cli info

# Lister les canaux actifs
./daznode-cli channels list

# Lister tous les canaux
./daznode-cli channels list --all
```

### Métriques et statistiques

```bash
# Collecter les métriques du nœud
./daznode-cli metrics collect

# Créer un snapshot quotidien
./daznode-cli metrics collect --daily

# Exporter les métriques en JSON
./daznode-cli metrics collect --export json
```

### Visualisations

```bash
# Générer un dataset de graphe réseau
./daznode-cli viz network

# Exporter au format JSON
./daznode-cli viz network --export json --output network.json

# Générer une heatmap de routage (par heure, jour ou semaine)
./daznode-cli viz heatmap --resolution hour

# Générer des recommandations d'optimisation de frais
./daznode-cli viz fees
```

### Analyse du réseau

```bash
# Afficher les statistiques globales du réseau Lightning
./daznode-cli network stats

# Afficher les détails d'un nœud spécifique
./daznode-cli network node 03abcdef...
```

## API REST

Daznode expose également ses fonctionnalités via une API REST, ce qui permet l'intégration avec d'autres applications ou la création d'interfaces utilisateur personnalisées.

### Lancement du serveur API

```bash
# Lancer l'API sur localhost:8000
./run_api.py

# Lancer l'API sur une interface et un port spécifiques
./run_api.py --host 0.0.0.0 --port 8080

# Activer le mode développement avec rechargement automatique
./run_api.py --reload
```

### Endpoints de l'API

L'API est documentée automatiquement et accessible via l'interface Swagger UI à l'adresse `/docs` ou ReDoc à l'adresse `/redoc`.

Voici quelques endpoints principaux :

#### Informations sur le nœud
- `GET /api/v1/node/info` - Informations sur le nœud
- `GET /api/v1/node/metrics` - Métriques du nœud
- `GET /api/v1/status` - État du nœud et des services

#### Canaux
- `GET /api/v1/channels` - Liste des canaux
- `GET /api/v1/channels/metrics` - Métriques des canaux
- `GET /api/v1/channels/performance` - Performance des canaux

#### Forwarding
- `GET /api/v1/forwarding` - Historique de forwarding
- `GET /api/v1/forwarding/metrics` - Métriques de forwarding
- `GET /api/v1/forwarding/heatmap` - Heatmap de routage

#### Optimisation
- `GET /api/v1/optimization/fees` - Suggestions d'optimisation de frais

#### Réseau
- `GET /api/v1/network/graph` - Graphe du réseau local
- `GET /api/v1/network/stats` - Statistiques du réseau
- `GET /api/v1/network/node/{pubkey}` - Détails d'un nœud spécifique

#### Métriques et rapports
- `POST /api/v1/metrics/snapshot` - Créer un snapshot quotidien
- `GET /api/v1/reports/{report_type}` - Générer un rapport périodique

## Modules

- **lnd_client.py** : Client pour interagir avec un nœud LND
- **lnrouter_client.py** : Client pour l'API LNRouter.app
- **metrics_collector.py** : Collecteur de métriques pour le nœud
- **node_aggregator.py** : Agrégateur de données sur les nœuds et canaux
- **visualization_exporter.py** : Exportateur pour visualisations et dashboards
- **cli.py** : Interface en ligne de commande
- **api.py** : API REST avec FastAPI

## Contributions

Les contributions sont bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## Licence

Ce projet est sous licence MIT.

# Daznode
