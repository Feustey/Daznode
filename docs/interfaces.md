# Interfaces de Daznode

Ce document décrit les principales interfaces utilisateur de Daznode.

## Tableau de bord principal

Le tableau de bord principal est la page d'accueil de l'application. Il affiche une vue d'ensemble des performances de votre nœud Lightning.

### Composants

- **NodeHeader** - Affiche le nom du nœud, le statut et les informations de base
- **StatsGrid** - Grille des statistiques principales (capacité, canaux, revenus)
- **NodeIdentifiers** - Affiche les identifiants du nœud (clé publique, adresse Tor)
- **HistoricalCharts** - Graphiques d'évolution des métriques dans le temps
- **LiveIndicator** - Indicateur de mise à jour en temps réel des données

### Fonctionnalités

- Vue d'ensemble rapide des KPIs
- Visualisation de l'évolution historique
- Indicateurs de tendance (hausse/baisse)
- Mises à jour en temps réel pour les métriques clés

### Capture d'écran

*Capture d'écran à venir - Une image du tableau de bord sera ajoutée ici*

## Vue des canaux

La vue des canaux permet d'analyser et de gérer l'ensemble des canaux Lightning de votre nœud.

### Composants

- **ChannelsTable** - Tableau listant tous les canaux avec leurs métriques
- **ChannelDetails** - Affichage détaillé d'un canal sélectionné
- **ChannelPerformanceChart** - Graphique de performance d'un canal spécifique
- **LiquidityManagement** - Interface de gestion de la liquidité des canaux

### Fonctionnalités

- Filtrage et tri des canaux selon différents critères
- Analyse détaillée des performances de chaque canal
- Visualisation de la distribution de liquidité
- Actions de gestion (fermeture, rééquilibrage)

## Vue d'analyse du réseau

La vue d'analyse du réseau permet de visualiser et d'explorer le réseau Lightning autour de votre nœud.

### Composants

- **NetworkGraph** - Visualisation interactive du graphe du réseau
- **NodeSearch** - Recherche de nœuds spécifiques
- **NetworkMetrics** - Métriques globales du réseau Lightning
- **PotentialPeers** - Suggestions de nouveaux pairs potentiels

### Fonctionnalités

- Exploration visuelle du réseau Lightning
- Zoom et navigation dans le graphe
- Sélection et analyse de nœuds spécifiques
- Suggestions de connexions optimales

## Vue d'optimisation

La vue d'optimisation propose des recommandations pour améliorer les performances de votre nœud.

### Composants

- **FeeOptimizationTable** - Recommandations d'optimisation des frais
- **ChannelBalanceChart** - Visualisation de l'équilibre des canaux
- **RevenueProjection** - Projection des revenus après optimisation
- **OptimizationActions** - Actions à entreprendre pour optimiser

### Fonctionnalités

- Recommandations personnalisées
- Simulation d'impact des changements
- Application directe des recommandations
- Historique des optimisations précédentes

## Interface du Bot IA

L'interface du Bot IA permet d'accéder aux recommandations avancées basées sur l'intelligence artificielle.

### Composants

- **AIChat** - Interface de conversation avec le bot IA
- **RecommendationCards** - Cartes de recommandations générées par l'IA
- **PaymentInterface** - Interface de paiement Lightning pour les fonctionnalités premium
- **AIInsights** - Analyses approfondies du nœud par l'IA

### Fonctionnalités

- Conversation naturelle avec le bot
- Recommandations personnalisées
- Paiement via NWC (Nostr Wallet Connect)
- Explications détaillées des recommandations

## Paramètres

La page des paramètres permet de configurer l'application selon vos préférences.

### Composants

- **GeneralSettings** - Paramètres généraux de l'application
- **InterfaceSettings** - Configuration de l'interface utilisateur
- **NotificationSettings** - Configuration des notifications
- **APISettings** - Gestion des clés API et connexions externes

### Fonctionnalités

- Configuration de l'intervalle de rafraîchissement
- Activation/désactivation des mises à jour en temps réel
- Gestion des préférences d'affichage
- Configuration des connexions API externes 