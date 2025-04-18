import {
  Node,
  NetworkNode,
  NetworkChannel,
  NetworkStats,
} from "../types/network";
import { NodeInfo } from "../types/mcpService";
import { mcpService } from "./mcpService";

export class NodeService {
  // Récupérer tous les nœuds
  async getNodes(): Promise<Node[]> {
    try {
      const response = await fetch(`${process.env.MCP_API_URL}/nodes`);
      if (!response.ok) {
        throw new Error("Failed to fetch nodes");
      }
      const nodes: NodeInfo[] = await response.json();

      // Récupérer les statistiques des nœuds pour obtenir les informations de capacité
      const nodeStats = await Promise.all(
        nodes.map((node) => mcpService.getNodeStats(node.pubkey))
      );

      return nodes.map((nodeInfo, index) => {
        const stats = nodeStats[index] || {
          totalCapacity: 0,
          numberOfChannels: 0,
          averageChannelSize: 0,
        };

        return {
          publicKey: nodeInfo.pubkey,
          id: nodeInfo.pubkey,
          name: nodeInfo.alias,
          alias: nodeInfo.alias,
          color: nodeInfo.color,
          addresses: nodeInfo.addresses,
          lastUpdate: new Date(nodeInfo.lastUpdate),
          capacity: stats.totalCapacity,
          channelCount: stats.numberOfChannels,
          avgChannelSize: stats.averageChannelSize,
          channels: [],
          age: this.calculateAge(new Date(nodeInfo.lastUpdate)),
          status: "active" as const,
        };
      });
    } catch (error) {
      console.error("Error fetching nodes:", error);
      throw error;
    }
  }

  // Récupérer les détails d'un nœud
  async getNodeDetails(pubkey: string): Promise<NetworkNode | null> {
    try {
      const nodeInfo = await mcpService.getNodeInfo(pubkey);
      if (!nodeInfo) return null;

      // Récupérer les statistiques du nœud
      const stats = await mcpService.getNodeStats(pubkey);

      return {
        publicKey: nodeInfo.pubkey,
        alias: nodeInfo.alias,
        color: nodeInfo.color,
        addresses: nodeInfo.addresses,
        lastUpdate: new Date(nodeInfo.lastUpdate),
        capacity: stats?.totalCapacity || 0,
        channelCount: stats?.numberOfChannels || 0,
        avgChannelSize: stats?.averageChannelSize || 0,
        city: undefined,
        country: undefined,
        isp: undefined,
        platform: undefined,
        betweennessRank: undefined,
        eigenvectorRank: undefined,
        closenessRank: undefined,
        avgFeeRate: undefined,
        uptime: stats?.uptime,
      };
    } catch (error) {
      console.error("Error fetching node details from MCP:", error);
      throw error;
    }
  }

  // Récupérer les canaux d'un nœud
  async getNodeChannels(nodeId: string): Promise<NetworkChannel[]> {
    try {
      const channels = await mcpService.getNodeChannels(nodeId);

      return channels.map((channel: any) => ({
        channelId: channel.id,
        node1Pub: channel.node1Id,
        node2Pub: channel.node2Id,
        capacity: channel.capacity || 0,
        lastUpdate: new Date(channel.timestamp),
        status: channel.status || "active",
      }));
    } catch (error) {
      console.error("Error fetching node channels from MCP:", error);
      throw error;
    }
  }

  // Récupérer les statistiques du réseau
  async getNetworkStats(): Promise<NetworkStats> {
    try {
      // Utiliser MCP pour récupérer les statistiques du réseau
      const networkStats = await mcpService.getNodeStats("network");

      // Récupérer les nœuds pour les statistiques par pays
      const nodes = await this.getNodes();

      // Calculer les statistiques par pays
      const nodesByCountry = nodes.reduce(
        (acc: Record<string, number>, node) => {
          const country = node.country || "unknown";
          acc[country] = (acc[country] || 0) + 1;
          return acc;
        },
        {} as Record<string, number>
      );

      // Récupérer l'historique des capacités
      const capacityHistory = await this.getCapacityHistory();

      return {
        totalNodes: networkStats.totalNodes || 0,
        totalChannels: networkStats.totalChannels || 0,
        totalCapacity: (networkStats.totalCapacity || 0).toString(),
        avgChannelSize: (networkStats.avgChannelSize || 0).toString(),
        avgCapacityPerChannel: networkStats.avgChannelSize || 0,
        avgChannelsPerNode:
          networkStats.totalChannels && networkStats.totalNodes
            ? networkStats.totalChannels / networkStats.totalNodes
            : 0,
        topNodes: nodes.slice(0, 10),
        recentChannels: nodes.slice(10, 20).map((node) => ({
          channelId: node.publicKey,
          node1Pub: "",
          node2Pub: node.publicKey,
          capacity: node.capacity,
          lastUpdate: node.lastUpdate,
          status: "active" as const,
        })),
        nodesByCountry,
        capacityHistory,
      };
    } catch (error) {
      console.error("Error fetching network stats from MCP:", error);
      throw error;
    }
  }

  // Récupérer l'historique des capacités
  async getCapacityHistory(): Promise<{ date: Date; value: number }[]> {
    try {
      // Utiliser MCP pour récupérer l'historique des capacités
      const history = await mcpService.getNodeStats("history");

      return history.map((item: any) => ({
        date: new Date(item.timestamp),
        value: item.capacity || 0,
      }));
    } catch (error) {
      console.error("Error fetching capacity history from MCP:", error);
      return [];
    }
  }

  // Fonction utilitaire pour calculer l'âge d'un nœud en jours
  calculateAge(createdAt: Date): number {
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - createdAt.getTime());
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  }

  // Fonction utilitaire pour formater l'âge en texte lisible
  formatAge(days: number): string {
    if (days < 30) {
      return `${days} jours`;
    } else if (days < 365) {
      const months = Math.floor(days / 30);
      return `${months} mois`;
    } else {
      const years = Math.floor(days / 365);
      return `${years} an${years > 1 ? "s" : ""}`;
    }
  }

  // Rechercher des nœuds par alias ou clé publique
  async searchNodes(query: string): Promise<Node[]> {
    try {
      const nodes = await this.getNodes();
      const lowerQuery = query.toLowerCase();

      return nodes.filter((node) => {
        const matchesAlias = node.alias.toLowerCase().includes(lowerQuery);
        const matchesPubkey = node.publicKey.toLowerCase().includes(lowerQuery);
        return matchesAlias || matchesPubkey;
      });
    } catch (error) {
      console.error("Error searching nodes:", error);
      throw error;
    }
  }
}

export const nodeService = new NodeService();

// Exporter la fonction searchNodes pour une utilisation directe
export const searchNodes = (query: string) => nodeService.searchNodes(query);
