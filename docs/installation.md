# Guide d'installation de Daznode

Ce document décrit les étapes nécessaires pour installer et configurer Daznode.

## Prérequis

- Python 3.9+
- Node.js 16+ (pour le frontend)
- Nœud Lightning (LND, c-lightning, etc.)
- Accès à l'API MCP (optionnel mais recommandé)

## Installation standard

### 1. Cloner le dépôt

```bash
git clone https://github.com/yourusername/daznode.git
cd daznode
```

### 2. Configurer l'environnement Python

```bash
# Créer un environnement virtuel
python -m venv .venv

# Activer l'environnement
# Sur Linux/macOS
source .venv/bin/activate
# Sur Windows
.venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configurer les variables d'environnement

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer le fichier .env avec vos propres configurations
```

Voici les principales variables à configurer :

```
# Configuration LND
LND_HOST=127.0.0.1
LND_PORT=10009
LND_CERT_PATH=/path/to/tls.cert
LND_MACAROON_PATH=/path/to/admin.macaroon

# Configuration API
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
SECRET_KEY=your-secret-key

# Configuration MCP (optionnel)
MCP_API_URL=https://api.mcp.example.com
MCP_API_KEY=your-mcp-api-key

# Configuration de la base de données
DATABASE_URL=postgresql://username:password@localhost/daznode
```

### 4. Initialiser la base de données

```bash
# Si vous utilisez une base de données PostgreSQL
python -m alembic upgrade head
```

### 5. Lancer l'API backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera accessible à l'adresse : http://localhost:8000

### 6. Installer et configurer le frontend (optionnel)

```bash
# Accéder au répertoire frontend
cd frontend

# Installer les dépendances
npm install

# Configurer le frontend
cp .env.local.example .env.local
# Éditer .env.local avec l'URL de votre API

# Lancer le serveur de développement
npm run dev
```

Le frontend sera accessible à l'adresse : http://localhost:3000

## Installation avec Docker

### 1. Cloner le dépôt

```bash
git clone https://github.com/yourusername/daznode.git
cd daznode
```

### 2. Configurer les variables d'environnement

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer le fichier .env avec vos propres configurations
```

### 3. Construire et lancer les conteneurs Docker

```bash
docker-compose up -d
```

L'API sera accessible à l'adresse : http://localhost:8000
Le frontend sera accessible à l'adresse : http://localhost:3000

## Installation sur Umbrel

Daznode est compatible avec Umbrel, ce qui simplifie grandement l'installation.

### 1. Ajouter le dépôt d'applications

Dans l'interface Umbrel, allez dans "App Store" puis "Add Community App Repository" et ajoutez :

```
https://github.com/yourusername/umbrel-daznode
```

### 2. Installer l'application

Recherchez "Daznode" dans l'App Store et cliquez sur "Install".

### 3. Configuration

Après l'installation, ouvrez Daznode et suivez les instructions de configuration initiale.

## Vérification de l'installation

Pour vérifier que l'installation fonctionne correctement :

1. Accédez à l'API : http://localhost:8000/health
   - Vous devriez recevoir une réponse `{"status": "ok"}`

2. Accédez à la documentation de l'API : http://localhost:8000/api/v1/docs
   - Vous devriez voir la documentation interactive Swagger

3. Si vous avez installé le frontend, accédez à : http://localhost:3000
   - Vous devriez voir le tableau de bord Daznode

## Dépannage

### Problèmes de connexion à LND

Vérifiez que :
- Le nœud LND est en cours d'exécution
- Les chemins des certificats TLS et macaroon sont correctement configurés
- Les autorisations des fichiers sont correctes

### Problèmes d'API

Vérifiez les journaux de l'API :
```bash
tail -f logs/daznode.log
```

### Problèmes de frontend

Vérifiez que :
- L'URL de l'API est correctement configurée dans `.env.local`
- Le serveur API est accessible depuis le frontend 