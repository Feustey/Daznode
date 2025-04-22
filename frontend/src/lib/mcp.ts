import axios from 'axios';

export class MCPService {
  private baseUrl: string;
  private apiKey: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_MCP_API_URL || '';
    this.apiKey = process.env.NEXT_PUBLIC_MCP_API_KEY || '';
  }

  private getHeaders() {
    return {
      'Authorization': `Bearer ${this.apiKey}`,
      'Content-Type': 'application/json',
    };
  }

  async get_channels_performance(timeframe: string) {
    try {
      const response = await axios.get(`${this.baseUrl}/channels/performance`, {
        headers: this.getHeaders(),
        params: { timeframe },
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des performances des canaux:', error);
      throw error;
    }
  }

  async get_network_stats() {
    try {
      const response = await axios.get(`${this.baseUrl}/network/stats`, {
        headers: this.getHeaders(),
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des statistiques du réseau:', error);
      throw error;
    }
  }

  async get_network_map() {
    try {
      const response = await axios.get(`${this.baseUrl}/network/map`, {
        headers: this.getHeaders(),
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération de la carte du réseau:', error);
      throw error;
    }
  }

  async get_network_growth_trends() {
    try {
      const response = await axios.get(`${this.baseUrl}/network/trends`, {
        headers: this.getHeaders(),
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des tendances de croissance:', error);
      throw error;
    }
  }

  async get_node_details(node_id: string) {
    try {
      const response = await axios.get(`${this.baseUrl}/network/nodes/${node_id}`, {
        headers: this.getHeaders(),
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des détails du nœud:', error);
      throw error;
    }
  }

  async get_node_ranking(node_id: string) {
    try {
      const response = await axios.get(`${this.baseUrl}/network/nodes/${node_id}/ranking`, {
        headers: this.getHeaders(),
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération du classement du nœud:', error);
      throw error;
    }
  }
} 