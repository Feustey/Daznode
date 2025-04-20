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
} 