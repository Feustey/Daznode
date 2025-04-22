# Configuration Docker de Daznode

Ce document explique comment configurer et utiliser l'architecture Docker de Daznode.

## Architecture

L'application est divisée en plusieurs services :

1. **API** (`api`)
   - Service principal exposant l'API REST
   - Port : 8000
   - Dépend de Redis et MongoDB

2. **Redis** (`redis`)
   - Cache en mémoire
   - Port : 6379
   - Persistance activée

3. **MongoDB** (`mongodb`)
   - Base de données principale
   - Port : 27017
   - Persistance activée

4. **Collecteur de métriques** (`metrics-collector`)
   - Collecte et agrège les métriques
   - Dépend de l'API et Redis

5. **Monitoring** (`monitoring`)
   - Prometheus pour la surveillance
   - Port : 9090
   - Interface de consultation des métriques

6. **Grafana** (`grafana`)
   - Tableaux de bord de visualisation
   - Port : 3000
   - Dépend de Prometheus

## Volumes

Les données persistantes sont stockées dans les volumes suivants :

- `daznode_data` : Données de l'application
- `redis_data` : Données Redis
- `mongodb_data` : Données MongoDB
- `prometheus_data` : Données Prometheus
- `grafana_data` : Données Grafana

## Démarrage

1. **Configuration initiale**

```bash
# Créer le fichier .env si nécessaire
cp .env.example .env

# Construire les images
docker-compose build
```

2. **Démarrage des services**

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier l'état des services
docker-compose ps
```

3. **Arrêt des services**

```bash
# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

## Surveillance

### Prometheus

- URL : http://localhost:9090
- Configuration : `prometheus.yml`
- Métriques disponibles :
  - `daznode_api_requests_total`
  - `daznode_api_response_time`
  - `daznode_metrics_collected`
  - etc.

### Grafana

- URL : http://localhost:3000
- Identifiants par défaut :
  - Utilisateur : admin
  - Mot de passe : admin (à changer à la première connexion)

## Maintenance

### Sauvegarde des données

```bash
# Sauvegarder les volumes
docker run --rm -v daznode_data:/source -v $(pwd)/backups:/backup alpine tar -czf /backup/daznode_data.tar.gz -C /source .

# Restaurer les volumes
docker run --rm -v daznode_data:/target -v $(pwd)/backups:/backup alpine sh -c "rm -rf /target/* && tar -xzf /backup/daznode_data.tar.gz -C /target"
```

### Mise à jour

```bash
# Mettre à jour les images
docker-compose pull

# Redémarrer les services
docker-compose up -d
```

### Logs

```bash
# Voir les logs de tous les services
docker-compose logs -f

# Voir les logs d'un service spécifique
docker-compose logs -f api
```

## Dépannage

### Problèmes courants

1. **Services non accessibles**
   - Vérifier les logs : `docker-compose logs`
   - Vérifier l'état des conteneurs : `docker-compose ps`
   - Vérifier les healthchecks : `docker-compose ps`

2. **Problèmes de persistance**
   - Vérifier les permissions des volumes
   - Vérifier l'espace disque disponible
   - Vérifier les logs des services de base de données

3. **Problèmes de performance**
   - Vérifier l'utilisation des ressources : `docker stats`
   - Ajuster les limites de ressources dans `docker-compose.yml`
   - Optimiser les requêtes de base de données

## Sécurité

1. **Configuration sécurisée**
   - Changer les mots de passe par défaut
   - Limiter l'accès aux ports exposés
   - Utiliser des réseaux Docker séparés

2. **Mises à jour de sécurité**
   - Mettre à jour régulièrement les images
   - Surveiller les vulnérabilités connues
   - Appliquer les correctifs de sécurité

3. **Backup et restauration**
   - Sauvegarder régulièrement les données
   - Tester les procédures de restauration
   - Documenter les procédures d'urgence 