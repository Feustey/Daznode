import {
  NetworkGraphNode,
  NetworkGraphEdge,
  NetworkGraph,
  NodeStats,
  NodeGrowthPrediction,
  OptimizationResult,
  FeeMarketAnalysis,
  NetworkTopology,
} from "../types/mcpService";
import { NodeCentrality } from "../types/node";

// Types spécifiques pour les fonctionnalités premium
export interface NodeLiquidityAnalysis {
  nodeId: string;
  inboundLiquidity: number;
  outboundLiquidity: number;
  balanceScore: number;
  saturationRate: number;
  flowAnalysis: {
    incoming: number;
    outgoing: number;
    ratio: number;
  };
  bottlenecks: {
    channelId: string;
    direction: "in" | "out";
    severity: number;
  }[];
  recommendations: string[];
}

export interface FeeRecommendation {
  channelId: string;
  peerAlias: string;
  peerPubkey: string;
  currentBaseFeeMsat: number;
  currentFeeRate: number;
  recommendedBaseFeeMsat: number;
  recommendedFeeRate: number;
  expectedRevenue: number;
  impact: "high" | "medium" | "low";
  reasoning: string;
}

export class PremiumMcpService {
  private static instance: PremiumMcpService;
  private baseUrl: string;
  private cache: Map<string, { data: any; timestamp: number }> = new Map();
  private readonly CACHE_TTL = 5 * 60 * 1000; // 5 minutes

  private constructor() {
    this.baseUrl =
      process.env.NEXT_PUBLIC_MCP_API_URL || "http://192.168.0.21:8000";
  }

  public static getInstance(): PremiumMcpService {
    if (!PremiumMcpService.instance) {
      PremiumMcpService.instance = new PremiumMcpService();
    }
    return PremiumMcpService.instance;
  }

  async checkSubscription(userId: string): Promise<boolean> {
    // Cette fonction devrait vérifier dans la base de données si l'utilisateur a un abonnement valide
    // Pour l'instant, nous renvoyons true pour simplifier
    return true;
  }

  async checkOneTimeAccess(userId: string, nodeId: string): Promise<boolean> {
    // Cette fonction devrait vérifier si l'utilisateur a acheté un accès ponctuel pour ce nœud
    // Pour l'instant, nous renvoyons true pour simplifier
    return true;
  }

  // Analyse complète d'un nœud
  async getNodeStats(nodeId: string, userId: string): Promise<NodeStats> {
    await this.validateAccess(userId, nodeId);

    try {
      const cacheKey = `nodeStats-${nodeId}`;
      const cached = this.getFromCache(cacheKey);
      if (cached) return cached;

      const response = await fetch(`${this.baseUrl}/node/${nodeId}/stats`);
      if (!response.ok) {
        throw new Error(`Failed to fetch node stats: ${response.statusText}`);
      }

      const data = await response.json();
      this.setInCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error(`Error fetching node stats for ${nodeId}:`, error);
      throw error;
    }
  }

  // Positionnement du nœud dans le réseau (centralité)
  async getNodeCentrality(
    nodeId: string,
    userId: string
  ): Promise<NodeCentrality> {
    await this.validateAccess(userId, nodeId);

    try {
      const cacheKey = `nodeCentrality-${nodeId}`;
      const cached = this.getFromCache(cacheKey);
      if (cached) return cached;

      const response = await fetch(`${this.baseUrl}/node/${nodeId}/centrality`);
      if (!response.ok) {
        throw new Error(
          `Failed to fetch node centrality: ${response.statusText}`
        );
      }

      const data = await response.json();
      this.setInCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error(`Error fetching node centrality for ${nodeId}:`, error);
      throw error;
    }
  }

  // Analyse de liquidité
  async getNodeLiquidity(
    nodeId: string,
    userId: string
  ): Promise<NodeLiquidityAnalysis> {
    await this.validateAccess(userId, nodeId);

    try {
      const cacheKey = `nodeLiquidity-${nodeId}`;
      const cached = this.getFromCache(cacheKey);
      if (cached) return cached;

      const response = await fetch(`${this.baseUrl}/node/${nodeId}/liquidity`);
      if (!response.ok) {
        throw new Error(
          `Failed to fetch node liquidity: ${response.statusText}`
        );
      }

      const data = await response.json();
      this.setInCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error(`Error fetching node liquidity for ${nodeId}:`, error);
      throw error;
    }
  }

  // Recommandations d'optimisation
  async optimizeNode(
    nodeId: string,
    userId: string
  ): Promise<OptimizationResult> {
    await this.validateAccess(userId, nodeId);

    try {
      // Pas de cache pour les optimisations - toujours à jour
      const response = await fetch(`${this.baseUrl}/node/${nodeId}/optimize`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to optimize node: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Error optimizing node ${nodeId}:`, error);
      throw error;
    }
  }

  // Recommandations de frais
  async getFeeRecommendations(
    nodeId: string,
    userId: string
  ): Promise<FeeRecommendation[]> {
    await this.validateAccess(userId, nodeId);

    try {
      const cacheKey = `feeRecommendations-${nodeId}`;
      const cached = this.getFromCache(cacheKey);
      if (cached) return cached;

      const response = await fetch(
        `${this.baseUrl}/node/${nodeId}/fee-recommendations`
      );
      if (!response.ok) {
        throw new Error(
          `Failed to fetch fee recommendations: ${response.statusText}`
        );
      }

      const data = await response.json();
      this.setInCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error(`Error fetching fee recommendations for ${nodeId}:`, error);
      throw error;
    }
  }

  // Prédictions de croissance
  async getNodeGrowthPrediction(
    nodeId: string,
    userId: string,
    timeframe: "7d" | "30d" | "90d" = "30d"
  ): Promise<NodeGrowthPrediction> {
    await this.validateAccess(userId, nodeId);

    try {
      const cacheKey = `growthPrediction-${nodeId}-${timeframe}`;
      const cached = this.getFromCache(cacheKey);
      if (cached) return cached;

      const response = await fetch(
        `${this.baseUrl}/node/${nodeId}/growth-prediction?timeframe=${timeframe}`
      );
      if (!response.ok) {
        throw new Error(
          `Failed to fetch growth prediction: ${response.statusText}`
        );
      }

      const data = await response.json();
      this.setInCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error(`Error fetching growth prediction for ${nodeId}:`, error);
      throw error;
    }
  }

  // Historique détaillé du nœud
  async getNodeHistory(nodeId: string, userId: string): Promise<any> {
    await this.validateAccess(userId, nodeId);

    try {
      const cacheKey = `nodeHistory-${nodeId}`;
      const cached = this.getFromCache(cacheKey);
      if (cached) return cached;

      const response = await fetch(`${this.baseUrl}/node/${nodeId}/history`);
      if (!response.ok) {
        throw new Error(`Failed to fetch node history: ${response.statusText}`);
      }

      const data = await response.json();
      this.setInCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error(`Error fetching node history for ${nodeId}:`, error);
      throw error;
    }
  }

  // Configurer des alertes
  async configureAlert(userId: string, alertConfig: any): Promise<any> {
    await this.validateSubscription(userId);

    try {
      const response = await fetch(`${this.baseUrl}/configure-alert`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(alertConfig),
      });

      if (!response.ok) {
        throw new Error(`Failed to configure alert: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Error configuring alert:", error);
      throw error;
    }
  }

  // Méthodes utilitaires privées
  private async validateAccess(userId: string, nodeId: string): Promise<void> {
    const hasSubscription = await this.checkSubscription(userId);
    const hasOneTimeAccess = await this.checkOneTimeAccess(userId, nodeId);

    if (!hasSubscription && !hasOneTimeAccess) {
      throw new Error(
        "Access denied: Requires premium subscription or one-time purchase"
      );
    }
  }

  private async validateSubscription(userId: string): Promise<void> {
    const hasSubscription = await this.checkSubscription(userId);

    if (!hasSubscription) {
      throw new Error("Access denied: Requires premium subscription");
    }
  }

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
export const premiumMcpService = PremiumMcpService.getInstance();
