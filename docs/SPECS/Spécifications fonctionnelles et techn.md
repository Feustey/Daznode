# Spécifications fonctionnelles et techniques pour Daznode

## 1. Stratégie d'accès aux données dans l'environnement Umbrel

### 1.1 Mise en cache persistante du graphe LN

#### Spécification fonctionnelle
- Le graphe du réseau Lightning Network doit être persisté sur disque entre les redémarrages du conteneur.
- Le cache doit être invalidé automatiquement après une durée configurable (par défaut 12h).
- En cas d'échec de récupération en direct, le système doit automatiquement utiliser le cache persistant.
- Le volume de cache doit être monté sur un volume Docker externe au conteneur.

#### Spécification technique
- Mise en place d'un système de cache à deux niveaux :
  - Niveau 1 : Cache en mémoire (déjà implémenté).
  - Niveau 2 : Cache persistant via SQLite pour le graphe complet, en utilisant un fichier monté via volume Docker.

```python
# Exemple d'utilisation SQLite pour cache persistant
def save_graph_to_sqlite(graph_data, db_path="/data/graph_cache.sqlite"):
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute("CREATE TABLE IF NOT EXISTS graph (data TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
        conn.execute("DELETE FROM graph")
        conn.execute("INSERT INTO graph (data) VALUES (?)", (json.dumps(graph_data),))
    conn.close()
```

## 2. Système de health check pour les sources de données

#### Spécification fonctionnelle
- Mécanisme de vérification d'état pour chaque source de données.
- Factory capable de basculer automatiquement entre les sources selon leur disponibilité.
- Fourniture de métriques de disponibilité via API.
- Résilience en cas de déconnexion temporaire de LND.

#### Spécification technique
- Classe `HealthCheckManager` chargée de tester les sources toutes les 60s (configurable).
- Intégration à `DataSourceFactory` pour sélection intelligente des sources.
- Endpoint `/api/v1/system/health` exposant l'état des sources.

```python
class HealthCheckManager:
    def __init__(self, sources):
        self.sources = sources

    def check(self):
        results = {}
        for name, source in self.sources.items():
            try:
                results[name] = source.ping()
            except Exception:
                results[name] = False
        return results
```

## 3. Tests unitaires pour les implémentations `DataSourceInterface`

#### Spécification fonctionnelle
- Suite de tests unitaires pour chaque source : LND, MCP, LNRouter.
- Utilisation de mocks pour les clients backend.
- Tests des cas d'erreur et fallback.
- Couverture des variations de configuration.

#### Spécification technique
- Mocks de clients `LNDClientMock`, `LNRouterClientMock`, etc.
- Tests de la logique `DataSourceFactory`, incluant fallback automatique.
- Utilisation de `pytest` et `unittest.mock` pour les tests.

```python
def test_datasource_factory_with_fallback():
    primary = Mock()
    fallback = Mock()
    primary.get_data.side_effect = Exception("primary failed")
    fallback.get_data.return_value = "fallback result"

    factory = DataSourceFactory([primary, fallback])
    result = factory.get_data()
    assert result == "fallback result"
```

## 4. Visualisation côté Umbrel UI

#### Spécification fonctionnelle
- Exposition des données dans l'interface Umbrel via dashboard HTML.
- Export de graphiques statiques (SVG).
- Intégration directe via iframe ou API REST.
- Documentation pour l'intégration à l'UI Umbrel.

#### Spécification technique
- Classe `UmbrelUIExporter` pour la génération de graphiques avec `matplotlib`.
- Endpoint `/umbrel-ui/dashboard` pour dashboard HTML.
- Endpoint `/umbrel-ui/api/stats` pour données en JSON.

```python
@app.get("/umbrel-ui/api/stats")
def stats():
    return generate_statistics()

@app.get("/umbrel-ui/dashboard")
def dashboard():
    fig = render_dashboard()
    return HTMLResponse(content=fig_to_svg(fig), media_type="image/svg+xml")
```

## 5. Modularité Docker améliorée

#### Spécification fonctionnelle
- Découpage des composants critiques en services Docker distincts.
- Scalabilité et résilience accrue.
- Développement et test facilités.

#### Spécification technique
- `docker-compose.yml` refactoré avec services `api`, `redis`, `mongodb`, `metrics-collector`, etc.
- Volumes montés pour la persistance des données (`daznode_data`).
- Healthchecks Docker pour surveillance des services.

```yaml
version: '3.9'
services:
  api:
    build: ./api
    ports:
      - "8000:8000"
    volumes:
      - daznode_data:/data
    depends_on:
      - mongodb
      - redis

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  mongodb:
    image: mongo
    ports:
      - "27017:27017"
    volumes:
      - daznode_data:/data/db

  metrics-collector:
    build: ./metrics
    depends_on:
      - api
      - redis

volumes:
  daznode_data:
```

## 6. Supervision et alerting

#### Spécification fonctionnelle
- Surveillance de l’état des sources et des services Docker.
- Notification via webhook ou email en cas de défaillance.

#### Spécification technique
- Intégration de Prometheus + Grafana dans un conteneur `monitoring`.
- Exportation des métriques via `/metrics` (format Prometheus).
- Règles d’alerting personnalisées.

```python
@app.get("/metrics")
def metrics():
    return Response(generate_prometheus_metrics(), media_type="text/plain")
```

```yaml
  monitoring:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
```

```yaml
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    depends_on:
      - monitoring
```

## 7. Sécurité & authentification

#### Spécification fonctionnelle
- Protection des endpoints sensibles.
- Accès sécurisé pour l’interface d’administration.

#### Spécification technique
- Mise en place de JWT pour authentification API.
- Limitation du nombre de requêtes (rate limiting).
- Chiffrement TLS via reverse proxy (Caddy / Traefik).

```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/protected")
def protected_route(token: str = Depends(oauth2_scheme)):
    if not validate_token(token):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return {"secure": True}
```

---

## 8. À venir

- CI/CD (déploiement continu via GitHub Actions)
- API publique (contract first avec OpenAPI)
- Documentation utilisateur & développeur
- Intégration Ollama au lieu d’OpenAI pour les fonctions LLM

