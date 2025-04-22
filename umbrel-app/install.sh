#!/bin/bash

# Création des dossiers nécessaires
mkdir -p data/prometheus
mkdir -p data/grafana
mkdir -p data/cache

# Copie des fichiers de configuration
cp prometheus.yml data/prometheus/
cp alertmanager.yml data/prometheus/
cp -r grafana/provisioning data/grafana/

# Création du fichier .env
cat > .env << EOL
# Tokens de sécurité
JWT_TOKEN=your_jwt_token_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Chemins des données Umbrel
APP_DATA_DIR=/home/umbrel/umbrel/apps/daznode/data
LND_DATA_DIR=/home/umbrel/umbrel/apps/lnd/data

# Configuration LND
LND_GRPC_HOST=umbrel.local
LND_GRPC_PORT=10009

# Configuration des services
PROMETHEUS_DATA_DIR=/home/umbrel/umbrel/apps/daznode/data/prometheus
GRAFANA_DATA_DIR=/home/umbrel/umbrel/apps/daznode/data/grafana
EOL

# Configuration des permissions
chmod -R 755 data
chown -R umbrel:umbrel data

echo "Installation terminée. Veuillez éditer le fichier .env avec vos tokens avant de démarrer l'application." 