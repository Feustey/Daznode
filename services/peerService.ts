import { PeerOfPeer } from "../types/peer";
import { CentralityData } from "../types/mcpService";
import { mcpService } from "./mcpService";

export class PeerService {
  // Récupérer les pairs d'un nœud
  async getPeersOfPeer(nodeId: string): Promise<PeerOfPeer[]> {
    try {
      // Utiliser MCP pour récupérer les pairs d'un nœud
      const peers = await mcpService.getNodeChannels(nodeId);

      // Transformer les données MCP en format attendu par notre interface
      return peers.map((peer: any) => ({
        nodePubkey: nodeId,
        peerPubkey: peer.node2Id,
        channelId: peer.id,
        capacity: peer.capacity || 0,
        lastUpdate: new Date(peer.timestamp),
      }));
    } catch (error) {
      console.error("Error fetching peers from MCP:", error);
      throw error;
    }
  }

  // Créer un nouveau pair
  async createPeer(
    nodeId: string,
    peerId: string,
    capacity: number
  ): Promise<PeerOfPeer> {
    try {
      // Utiliser MCP pour créer un nouveau canal
      const channel = await mcpService.openChannel(nodeId, capacity, peerId);

      return {
        nodePubkey: nodeId,
        peerPubkey: peerId,
        channelId: channel.id,
        capacity: channel.capacity || 0,
        lastUpdate: new Date(channel.timestamp),
      };
    } catch (error) {
      console.error("Error creating peer with MCP:", error);
      throw error;
    }
  }

  // Supprimer un pair
  async deletePeer(channelId: string): Promise<boolean> {
    try {
      // Utiliser MCP pour fermer un canal
      const result = await mcpService.closeChannel(channelId);

      return result.success || false;
    } catch (error) {
      console.error("Error deleting peer with MCP:", error);
      throw error;
    }
  }

  // Récupérer les données de centralité d'un nœud
  async getCentralityData(nodeId: string): Promise<CentralityData> {
    try {
      // Utiliser MCP pour récupérer les données de centralité
      const nodeInfo = await mcpService.getNodeInfo(nodeId);
      const stats = await mcpService.getNodeStats(nodeId);

      return {
        betweenness: stats?.betweenness || 0,
        closeness: stats?.closeness || 0,
        degree: stats?.numberOfChannels || 0,
        eigenvector: stats?.eigenvector || 0,
      };
    } catch (error) {
      console.error("Error fetching centrality data from MCP:", error);
      throw error;
    }
  }

  // Récupérer les résultats d'optimisation pour un nœud
  async getOptimizationResults(nodeId: string): Promise<any> {
    try {
      // Utiliser MCP pour récupérer les résultats d'optimisation
      const nodeStats = await mcpService.getNodeStats(nodeId);

      return {
        recommendedChannels: nodeStats.recommendedChannels || [],
        potentialPartners: nodeStats.potentialPartners || [],
        timestamp: new Date(nodeStats.timestamp),
      };
    } catch (error) {
      console.error("Error fetching optimization results from MCP:", error);
      throw error;
    }
  }
}

export const peerService = new PeerService();
