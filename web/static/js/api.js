/**
 * API.js - Client JavaScript pour l'API Daznode
 * Ce module gère toutes les requêtes vers l'API REST Daznode
 */

class DaznodeAPI {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.connected = false;
        this.connecting = false;
        this.onConnectionStatusChange = null;
    }

    /**
     * Configure un callback pour les changements de statut de connexion
     * @param {Function} callback - Fonction à appeler lors des changements de statut
     */
    setConnectionStatusCallback(callback) {
        this.onConnectionStatusChange = callback;
    }

    /**
     * Modifie l'état de connexion et déclenche le callback si défini
     * @param {boolean} connected - État de connexion
     * @param {boolean} connecting - État de connexion en cours
     */
    _updateConnectionStatus(connected, connecting = false) {
        this.connected = connected;
        this.connecting = connecting;
        
        if (this.onConnectionStatusChange) {
            this.onConnectionStatusChange(connected, connecting);
        }
    }

    /**
     * Effectue une requête vers l'API
     * @param {string} endpoint - Point de terminaison de l'API
     * @param {string} method - Méthode HTTP (GET, POST, etc.)
     * @param {Object} data - Données à envoyer (pour POST/PUT)
     * @returns {Promise<Object>} - Réponse de l'API
     */
    async request(endpoint, method = 'GET', data = null) {
        const url = `${this.baseUrl}${endpoint}`;
        
        try {
            this._updateConnectionStatus(false, true);
            
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            };
            
            if (data && (method === 'POST' || method === 'PUT')) {
                options.body = JSON.stringify(data);
            }
            
            const response = await fetch(url, options);
            
            if (!response.ok) {
                const errorBody = await response.json().catch(() => ({}));
                throw new Error(errorBody.detail || `Erreur ${response.status}: ${response.statusText}`);
            }
            
            this._updateConnectionStatus(true, false);
            return await response.json();
        } catch (error) {
            this._updateConnectionStatus(false, false);
            console.error(`Erreur lors de la requête vers ${endpoint}:`, error);
            throw error;
        }
    }

    // ========== INFORMATIONS SUR LE NŒUD ==========
    
    /**
     * Récupère les informations sur le nœud
     * @returns {Promise<Object>} - Informations sur le nœud
     */
    async getNodeInfo() {
        return this.request('/node/info');
    }
    
    /**
     * Récupère le solde du nœud
     * @returns {Promise<Object>} - Solde du nœud
     */
    async getNodeBalance() {
        return this.request('/node/balance');
    }
    
    // ========== CANAUX ==========
    
    /**
     * Récupère la liste des canaux
     * @returns {Promise<Array>} - Liste des canaux
     */
    async getChannels() {
        return this.request('/channels');
    }
    
    /**
     * Récupère la liste des canaux enrichis avec des données additionnelles
     * @returns {Promise<Array>} - Liste des canaux enrichis
     */
    async getEnrichedChannels() {
        return this.request('/channels/enriched');
    }
    
    /**
     * Récupère des informations détaillées sur un canal spécifique
     * @param {string} channelId - Identifiant du canal
     * @returns {Promise<Object>} - Informations sur le canal
     */
    async getChannelInfo(channelId) {
        return this.request(`/channels/${channelId}`);
    }
    
    // ========== FORWARDING ==========
    
    /**
     * Récupère les statistiques de forwarding
     * @param {number} days - Nombre de jours à considérer
     * @returns {Promise<Object>} - Statistiques de forwarding
     */
    async getForwardingStats(days = 7) {
        return this.request(`/forwarding/stats?days=${days}`);
    }
    
    /**
     * Récupère l'historique des forwards
     * @param {number} limit - Limite du nombre d'entrées
     * @returns {Promise<Array>} - Historique des forwards
     */
    async getForwardingHistory(limit = 100) {
        return this.request(`/forwarding/history?limit=${limit}`);
    }
    
    // ========== OPTIMISATION ==========
    
    /**
     * Récupère des recommandations pour l'optimisation des canaux
     * @returns {Promise<Array>} - Recommandations d'optimisation
     */
    async getOptimizationRecommendations() {
        return this.request('/optimization/recommendations');
    }
    
    // ========== RÉSEAU ==========
    
    /**
     * Récupère des informations sur un nœud du réseau
     * @param {string} pubKey - Clé publique du nœud
     * @returns {Promise<Object>} - Informations sur le nœud
     */
    async getNetworkNode(pubKey) {
        return this.request(`/network/nodes/${pubKey}`);
    }
    
    /**
     * Recherche des nœuds sur le réseau
     * @param {string} query - Terme de recherche
     * @returns {Promise<Array>} - Résultats de recherche
     */
    async searchNetworkNodes(query) {
        return this.request(`/network/search?query=${encodeURIComponent(query)}`);
    }
    
    // ========== MÉTRIQUES ==========
    
    /**
     * Récupère les métriques quotidiennes
     * @param {string} date - Date (format YYYY-MM-DD)
     * @returns {Promise<Object>} - Métriques quotidiennes
     */
    async getDailyMetrics(date) {
        return this.request(`/metrics/daily${date ? `?date=${date}` : ''}`);
    }
    
    /**
     * Récupère l'historique des métriques
     * @param {number} days - Nombre de jours d'historique
     * @returns {Promise<Array>} - Historique des métriques
     */
    async getMetricsHistory(days = 30) {
        return this.request(`/metrics/history?days=${days}`);
    }
}

// Exporte une instance unique de l'API
const api = new DaznodeAPI(); 