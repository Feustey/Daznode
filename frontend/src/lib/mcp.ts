import axios from 'axios';

// Constantes pour l'environnement de développement
const USE_MOCK_DATA = false;
const LNBITS_URL = process.env.NEXT_PUBLIC_LNBITS_URL || 'http://192.168.0.45:5000';
const LNBITS_ADMIN_KEY = process.env.NEXT_PUBLIC_LNBITS_ADMIN_KEY || 'fddac5fb8bf64eec944c89255b98dac4';

export class MCPService {
  private baseUrl: string;
  private apiKey: string;

  constructor() {
    // Utiliser LNBits comme MCP API en développement
    this.baseUrl = process.env.NEXT_PUBLIC_MCP_API_URL || LNBITS_URL;
    this.apiKey = process.env.NEXT_PUBLIC_MCP_API_KEY || LNBITS_ADMIN_KEY;
    
    // Initialiser la connexion à LNBits
    if (!USE_MOCK_DATA) {
      this.connectToLNBits().then(result => {
        if (result) {
          console.log('Connexion LNBits établie au démarrage');
        } else {
          console.warn('Impossible de se connecter à LNBits au démarrage, utilisation des données mockées');
        }
      });
    }
  }

  private getHeaders() {
    return {
      'Authorization': `Bearer ${this.apiKey}`,
      'Content-Type': 'application/json',
    };
  }

  private getLNBitsHeaders() {
    return {
      'X-Api-Key': LNBITS_ADMIN_KEY,
      'Content-Type': 'application/json',
    };
  }

  async connectToLNBits() {
    if (!USE_MOCK_DATA) {
      try {
        const response = await axios.get(`${LNBITS_URL}/api/v1/wallet`, {
          headers: this.getLNBitsHeaders(),
        });
        console.log('Connexion à LNBits établie:', response.data);
        return response.data;
      } catch (error) {
        console.error('Erreur de connexion à LNBits:', error);
        return null;
      }
    }
    return null;
  }

  async get_channels_performance(timeframe: string) {
    if (USE_MOCK_DATA) {
      console.log('Utilisation des données mockées pour les performances des canaux');
      return this.getMockChannelsPerformance();
    }

    try {
      const response = await axios.get(`${this.baseUrl}/channels/performance`, {
        headers: this.getHeaders(),
        params: { timeframe },
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des performances des canaux:', error);
      return this.getMockChannelsPerformance();
    }
  }

  async get_network_stats() {
    if (USE_MOCK_DATA) {
      console.log('Utilisation des données mockées pour les statistiques du réseau');
      return this.getMockNetworkStats();
    }

    try {
      const response = await axios.get(`${this.baseUrl}/network/stats`, {
        headers: this.getHeaders(),
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des statistiques du réseau:', error);
      return this.getMockNetworkStats();
    }
  }

  async get_network_nodes(limit: number = 50) {
    if (USE_MOCK_DATA) {
      console.log('Utilisation des données mockées pour les nœuds du réseau');
      return this.getMockNetworkNodes(limit);
    }

    try {
      const response = await axios.get(`${this.baseUrl}/network/nodes`, {
        headers: this.getHeaders(),
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des nœuds du réseau:', error);
      return this.getMockNetworkNodes(limit);
    }
  }

  async get_network_map() {
    if (USE_MOCK_DATA) {
      console.log('Utilisation des données mockées pour la carte du réseau');
      return this.getMockNetworkMap();
    }

    try {
      const response = await axios.get(`${this.baseUrl}/network/map`, {
        headers: this.getHeaders(),
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération de la carte du réseau:', error);
      return this.getMockNetworkMap();
    }
  }

  async get_network_growth_trends() {
    if (USE_MOCK_DATA) {
      console.log('Utilisation des données mockées pour les tendances de croissance');
      return this.getMockNetworkGrowthTrends();
    }

    try {
      const response = await axios.get(`${this.baseUrl}/network/trends`, {
        headers: this.getHeaders(),
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des tendances de croissance:', error);
      return this.getMockNetworkGrowthTrends();
    }
  }

  async get_node_details(node_id: string) {
    if (USE_MOCK_DATA) {
      console.log('Utilisation des données mockées pour les détails du nœud');
      return this.getMockNodeDetails(node_id);
    }

    try {
      const response = await axios.get(`${this.baseUrl}/network/nodes/${node_id}`, {
        headers: this.getHeaders(),
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des détails du nœud:', error);
      return this.getMockNodeDetails(node_id);
    }
  }

  async get_node_ranking(node_id: string) {
    if (USE_MOCK_DATA) {
      console.log('Utilisation des données mockées pour le classement du nœud');
      return this.getMockNodeRanking(node_id);
    }

    try {
      const response = await axios.get(`${this.baseUrl}/network/nodes/${node_id}/ranking`, {
        headers: this.getHeaders(),
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération du classement du nœud:', error);
      return this.getMockNodeRanking(node_id);
    }
  }

  // Méthodes pour les données mockées
  private getMockNetworkStats() {
    return {
      nodes_count: 18632,
      channels_count: 111457,
      total_capacity: 4521325600000,
      avg_capacity_per_channel: 40565800,
      avg_fee_rate: 0.0000025,
      active_nodes_percent: 85.3,
      growth_last_month: {
        nodes: 3.2,
        channels: 5.8,
        capacity: 7.1
      }
    };
  }

  private getMockNetworkNodes(limit: number) {
    // Générer un nombre de nœuds mockés égal à la limite demandée
    const mockNodes = [];
    for (let i = 0; i < limit; i++) {
      mockNodes.push({
        pubkey: `node${i}${Math.random().toString(36).substring(2, 8)}`,
        alias: `Lightning Node ${i+1}`,
        num_channels: Math.floor(Math.random() * 100) + 1,
        total_capacity: Math.floor(Math.random() * 100000000) + 1000000,
        centrality_rank: Math.floor(Math.random() * 5000) + 1,
        uptime: Math.random() * 0.3 + 0.7, // Entre 0.7 et 1.0
        routing_volume: Math.floor(Math.random() * 20000000),
        last_update: new Date(Date.now() - Math.floor(Math.random() * 30) * 86400000).toISOString() // Entre aujourd'hui et il y a 30 jours
      });
    }
    return mockNodes;
  }

  private getMockChannelsPerformance() {
    return {
      channels: [
        { id: "123456:1", capacity: 3000000, local_balance: 2850000, remote_balance: 150000, status: "active", fee_rate: 0.000001, performance_score: 98 },
        { id: "123456:2", capacity: 5000000, local_balance: 2500000, remote_balance: 2500000, status: "active", fee_rate: 0.000002, performance_score: 95 },
        { id: "123456:3", capacity: 2000000, local_balance: 1000000, remote_balance: 1000000, status: "active", fee_rate: 0.000001, performance_score: 90 }
      ],
      total_routed_last_week: 3560000,
      total_fees_earned_last_week: 1800,
      most_active_channel: "123456:1",
      least_active_channel: "123456:3"
    };
  }

  private getMockNetworkMap() {
    return {
      nodes: [
        { id: "node1", alias: "ACINQ", capacity: 290000000, channels: 85, coordinates: { x: 0.3, y: 0.2 } },
        { id: "node2", alias: "LNBig", capacity: 320000000, channels: 93, coordinates: { x: 0.5, y: 0.4 } },
        { id: "node3", alias: "Bitfinex", capacity: 270000000, channels: 78, coordinates: { x: 0.7, y: 0.6 } }
      ],
      edges: [
        { source: "node1", target: "node2", capacity: 12000000 },
        { source: "node1", target: "node3", capacity: 8000000 },
        { source: "node2", target: "node3", capacity: 10000000 }
      ]
    };
  }

  private getMockNetworkGrowthTrends() {
    return {
      monthly_data: [
        { month: "Jan", nodes: 15200, channels: 95000, capacity: 3800000000000 },
        { month: "Feb", nodes: 16100, channels: 98500, capacity: 4000000000000 },
        { month: "Mar", nodes: 16900, channels: 102000, capacity: 4200000000000 },
        { month: "Apr", nodes: 17700, channels: 106800, capacity: 4400000000000 },
        { month: "May", nodes: 18632, channels: 111457, capacity: 4521325600000 }
      ],
      growth_rates: {
        yearly_nodes: 22.5,
        yearly_channels: 31.2,
        yearly_capacity: 38.7
      }
    };
  }

  private getMockNodeDetails(nodeId: string) {
    return {
      id: nodeId,
      alias: "Feustey Lightning",
      public_key: "02778f4a4eb3a2344b9fd8ee72e7ec5f03f803e5f5273e2e1a2af508910cf2b12b",
      color: "#3399ff",
      capacity: 17965032,
      channels: 12,
      connected_nodes: ["ACINQ", "LNBig", "Bitfinex"],
      uptime: 99.7,
      last_update: "2023-05-15T12:30:45Z"
    };
  }

  private getMockNodeRanking(nodeId: string) {
    return {
      capacity_rank: 1860,
      channels_rank: 1148,
      centrality_rank: 1523,
      historical_ranks: [
        { date: "2023-04-15", capacity_rank: 1861, channels_rank: 1151 },
        { date: "2023-04-22", capacity_rank: 1861, channels_rank: 1149 },
        { date: "2023-04-29", capacity_rank: 1860, channels_rank: 1148 },
        { date: "2023-05-06", capacity_rank: 1860, channels_rank: 1148 },
        { date: "2023-05-13", capacity_rank: 1860, channels_rank: 1148 }
      ]
    };
  }
} 