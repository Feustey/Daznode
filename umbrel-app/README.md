# Installation de DazNode sur Umbrel

## Prérequis
- Umbrel installé et fonctionnel
- LND actif et configuré
- Git installé

## Installation

1. Clonez le dépôt dans le dossier d'applications Umbrel :
```bash
cd ~/umbrel/apps
git clone https://github.com/Feustey/Daznode.git daznode
```

2. Exécutez le script d'installation :
```bash
cd daznode
chmod +x install.sh
./install.sh
```

3. Éditez le fichier `.env` généré et ajoutez vos tokens :
```
JWT_TOKEN=votre_token_jwt
TELEGRAM_BOT_TOKEN=votre_token_telegram
TELEGRAM_CHAT_ID=votre_chat_id
```

4. Installez l'application via l'interface Umbrel :
- Allez dans l'App Store Umbrel
- Cliquez sur "Install from URL"
- Entrez le chemin : `/home/umbrel/umbrel/apps/daznode`

## Structure des dossiers
- `data/` : Données persistantes
  - `prometheus/` : Configuration et données Prometheus
  - `grafana/` : Configuration et données Grafana
  - `cache/` : Cache de l'application

## Accès à l'application

- Interface principale : http://umbrel.local:8000
- Grafana : http://umbrel.local:3000
- Prometheus : http://umbrel.local:9090
- Métriques : http://umbrel.local:9100

## Support

En cas de problème, vous pouvez :
1. Consulter les logs : `docker-compose logs -f`
2. Ouvrir une issue sur GitHub : https://github.com/Feustey/Daznode/issues
3. Redémarrer l'application depuis l'interface Umbrel

## Mise à jour
Pour mettre à jour l'application :
```bash
cd ~/umbrel/apps/daznode
git pull
./install.sh
``` 