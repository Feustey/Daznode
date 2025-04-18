import { NetworkSummaryData } from "../types/node";
import { NetworkGraph, NetworkTopology } from "../types/mcpService";

export class BasicMcpService {
  private static instance: BasicMcpService;
  private baseUrl: string;
  private cache: Map<string, { data: any; timestamp: number }> = new Map();
  private readonly CACHE_TTL = 15 * 60 * 1000; // 15 minutes pour les données de base

  private constructor() {
    this.baseUrl =
      process.env.NEXT_PUBLIC_MCP_API_URL || "http://192.168.0.21:8000";
  }

  public static getInstance(): BasicMcpService {
    if (!BasicMcpService.instance) {
      BasicMcpService.instance = new BasicMcpService();
    }
    return BasicMcpService.instance;
  }

  // Récupérer les statistiques générales du réseau
  async getNetworkSummary(): Promise<NetworkSummaryData> {
    try {
      const cacheKey = "networkSummary";
      const cached = this.getFromCache(cacheKey);
      if (cached) return cached;

      const response = await fetch(`${this.baseUrl}/network-summary`);
      if (!response.ok) {
        throw new Error(
          `Failed to fetch network summary: ${response.statusText}`
        );
      }

      const data = await response.json();
      this.setInCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error("Error fetching network summary:", error);
      throw error;
    }
  }

  // Récupérer une version simplifiée du graphe réseau (limité aux nœuds importants)
  async getSimplifiedNetworkGraph(): Promise<NetworkGraph> {
    try {
      const cacheKey = "simplifiedNetworkGraph";
      const cached = this.getFromCache(cacheKey);
      if (cached) return cached;

      const response = await fetch(
        `${this.baseUrl}/network-graph?simplified=true&limit=500`
      );
      if (!response.ok) {
        throw new Error(
          `Failed to fetch simplified network graph: ${response.statusText}`
        );
      }

      const data = await response.json();
      this.setInCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error("Error fetching simplified network graph:", error);
      throw error;
    }
  }

  // Récupérer les données de centralité (version basique - top 20)
  async getTopCentralities(): Promise<any> {
    try {
      const cacheKey = "topCentralities";
      const cached = this.getFromCache(cacheKey);
      if (cached) return cached;

      const response = await fetch(`${this.baseUrl}/centralities?limit=20`);
      if (!response.ok) {
        throw new Error(
          `Failed to fetch top centralities: ${response.statusText}`
        );
      }

      const data = await response.json();
      this.setInCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error("Error fetching top centralities:", error);
      throw error;
    }
  }

  // Récupérer les statistiques générales des frais (anonymisées)
  async getFeeMarketOverview(): Promise<any> {
    try {
      const cacheKey = "feeMarketOverview";
      const cached = this.getFromCache(cacheKey);
      if (cached) return cached;

      const response = await fetch(`${this.baseUrl}/fee-market/overview`);
      if (!response.ok) {
        throw new Error(
          `Failed to fetch fee market overview: ${response.statusText}`
        );
      }

      const data = await response.json();
      this.setInCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error("Error fetching fee market overview:", error);
      throw error;
    }
  }

  // Récupérer les données historiques limitées (résolution journalière, 30 jours)
  async getLimitedHistoricalData(): Promise<any> {
    try {
      const cacheKey = "limitedHistoricalData";
      const cached = this.getFromCache(cacheKey);
      if (cached) return cached;

      const response = await fetch(
        `${this.baseUrl}/historical?resolution=daily&limit=30`
      );
      if (!response.ok) {
        throw new Error(
          `Failed to fetch limited historical data: ${response.statusText}`
        );
      }

      const data = await response.json();
      this.setInCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error("Error fetching limited historical data:", error);
      throw error;
    }
  }

  // Tester la connexion à l'API MCP
  async testConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return response.ok;
    } catch (error) {
      console.error("Error testing MCP connection:", error);
      return false;
    }
  }

  // Méthodes utilitaires privées
  private getFromCache(key: string): any {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
      return cached.data;
    }
    return null;
  }

  private setInCache(key: string, data: any): void {
    this.cache.set(key, { data, timestamp: Date.now() });
  }
}

// Export d'une instance singleton
export const basicMcpService = BasicMcpService.getInstance();
