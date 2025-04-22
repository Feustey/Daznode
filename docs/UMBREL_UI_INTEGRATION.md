# Intégration avec l'interface Umbrel

Ce document explique comment intégrer les visualisations Daznode dans l'interface Umbrel.

## Options d'intégration

### 1. Intégration via iframe

La méthode la plus simple est d'utiliser un iframe pour afficher le dashboard complet :

```html
<iframe 
    src="http://localhost:8000/umbrel-ui/dashboard" 
    width="100%" 
    height="800px" 
    frameborder="0"
></iframe>
```

### 2. Intégration via API

Pour une intégration plus personnalisée, vous pouvez utiliser les endpoints API :

- `/umbrel-ui/api/stats` : Récupère les statistiques réseau en JSON
- `/umbrel-ui/api/graph` : Récupère les données du graphe en JSON

Exemple d'utilisation :

```javascript
// Récupérer les statistiques
fetch('http://localhost:8000/umbrel-ui/api/stats')
    .then(response => response.json())
    .then(stats => {
        // Utiliser les statistiques
        console.log(stats);
    });

// Récupérer le graphe
fetch('http://localhost:8000/umbrel-ui/api/graph')
    .then(response => response.json())
    .then(graph => {
        // Utiliser les données du graphe
        console.log(graph);
    });
```

## Personnalisation

### Styles CSS

Le dashboard utilise des classes CSS que vous pouvez personnaliser :

```css
.daznode-container {
    /* Styles du conteneur principal */
}

.daznode-card {
    /* Styles des cartes */
}

.daznode-stats {
    /* Styles des statistiques */
}

.daznode-graph {
    /* Styles du graphe */
}
```

### Mise à jour automatique

Pour mettre à jour automatiquement les données, vous pouvez utiliser un intervalle :

```javascript
// Mettre à jour toutes les 5 minutes
setInterval(() => {
    // Recharger les données
    fetch('http://localhost:8000/umbrel-ui/api/stats')
        .then(response => response.json())
        .then(updateStats);
}, 300000);
```

## Bonnes pratiques

1. **Performance**
   - Utilisez la mise en cache côté client
   - Limitez la fréquence des mises à jour
   - Optimisez les requêtes API

2. **Sécurité**
   - Vérifiez les origines des requêtes
   - Utilisez HTTPS en production
   - Limitez l'accès aux endpoints sensibles

3. **UX**
   - Affichez des indicateurs de chargement
   - Gérez les erreurs de manière élégante
   - Fournissez des retours visuels pour les actions

## Dépannage

### Problèmes courants

1. **Dashboard non accessible**
   - Vérifiez que le service Daznode est en cours d'exécution
   - Vérifiez les logs pour les erreurs
   - Assurez-vous que le port 8000 est accessible

2. **Données non mises à jour**
   - Vérifiez la connexion aux sources de données
   - Vérifiez les permissions des fichiers de cache
   - Vérifiez les logs pour les erreurs de mise à jour

3. **Problèmes de style**
   - Vérifiez les conflits CSS
   - Assurez-vous que les polices sont accessibles
   - Vérifiez la compatibilité des navigateurs

## Support

Pour toute question ou problème, contactez l'équipe de support Daznode. 