import { Node, NetworkStats, NetworkNode } from "../types/network";

export interface NetworkMovement {
  id: string;
  name: string;
  capacity: string;
  capacityChange: string;
  channels: string;
  channelsChange: string;
  timestamp: string;
}

class NetworkService {
  private baseUrl: string;

  constructor() {
    this.baseUrl =
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000/api/network";
  }

  async getNetworkStats(): Promise<NetworkStats> {
    try {
      const response = await fetch(`${this.baseUrl}/stats`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("Error fetching network stats:", error);
      throw error;
    }
  }

  async getNodes(): Promise<NetworkNode[]> {
    try {
      const response = await fetch(`${this.baseUrl}/nodes`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("Error fetching nodes:", error);
      throw error;
    }
  }

  async getNodeDetails(nodeId: string): Promise<NetworkNode> {
    try {
      const response = await fetch(`${this.baseUrl}/nodes/${nodeId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("Error fetching node details:", error);
      throw error;
    }
  }

  async getNodeChannels(nodeId: string): Promise<any[]> {
    try {
      const response = await fetch(`${this.baseUrl}/nodes/${nodeId}/channels`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("Error fetching node channels:", error);
      throw error;
    }
  }

  async getTopNodes(
    period: "daily" | "weekly" | "monthly"
  ): Promise<NetworkNode[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/top-nodes?period=${period}`
      );
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("Error fetching top nodes:", error);
      throw error;
    }
  }

  async getNetworkMovements(
    period: "daily" | "weekly" | "monthly"
  ): Promise<NetworkMovement[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/movements?period=${period}`
      );
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("Error fetching network movements:", error);
      throw error;
    }
  }

  async searchNodes(query: string): Promise<NetworkNode[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/search?q=${encodeURIComponent(query)}`
      );
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("Error searching nodes:", error);
      throw error;
    }
  }
}

export const networkService = new NetworkService();
