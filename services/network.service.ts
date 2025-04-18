import { supabase } from "@/utils/supabase";

export interface NetworkStats {
  totalNodes: number;
  totalChannels: number;
  totalCapacity: number;
  avgCapacityPerChannel: number;
  avgChannelsPerNode: number;
  activeNodes: number;
  activeChannels: number;
  networkGrowth: {
    nodes: number;
    channels: number;
    capacity: number;
  };
  capacityHistory: any[];
  nodesByCountry: any[];
  lastUpdate: Date;
}

export const revalidate = 60; // Revalidation toutes les minutes

export async function getCurrentStats(): Promise<NetworkStats> {
  try {
    const { data: stats, error } = await supabase
      .from("network_stats")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(1)
      .single();

    if (error) {
      console.error("Error fetching network stats:", error);
      // Retourner des données de démonstration en cas d'erreur
      return {
        totalNodes: 15000,
        totalChannels: 85000,
        totalCapacity: 5000000000,
        avgCapacityPerChannel: 58823,
        avgChannelsPerNode: 5.67,
        activeNodes: 12000,
        activeChannels: 75000,
        networkGrowth: {
          nodes: 150,
          channels: 850,
          capacity: 50000000,
        },
        capacityHistory: [],
        nodesByCountry: [],
        lastUpdate: new Date(),
      };
    }

    return stats;
  } catch (error) {
    console.error("Error in getCurrentStats:", error);
    throw error;
  }
}

export async function getNetworkStats(): Promise<NetworkStats> {
  try {
    const { data: stats, error } = await supabase
      .from("network_stats")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(1)
      .single();

    if (error) {
      console.error("Error fetching network stats:", error);
      throw error;
    }

    return {
      totalNodes: stats.total_nodes,
      totalChannels: stats.total_channels,
      totalCapacity: stats.total_capacity,
      avgCapacityPerChannel: stats.avg_capacity_per_channel,
      avgChannelsPerNode: stats.avg_channels_per_node,
      activeNodes: stats.active_nodes,
      activeChannels: stats.active_channels,
      networkGrowth: {
        nodes: stats.nodes_growth,
        channels: stats.channels_growth,
        capacity: stats.capacity_growth,
      },
      capacityHistory: stats.capacity_history,
      nodesByCountry: stats.nodes_by_country,
      lastUpdate: new Date(stats.created_at),
    };
  } catch (error) {
    console.error("Error in getNetworkStats:", error);
    throw error;
  }
}

export async function getPeersOfPeers(nodeId: string): Promise<any[]> {
  try {
    const { data, error } = await supabase
      .from("node_peers")
      .select("*")
      .eq("node_id", nodeId);

    if (error) {
      console.error("Error fetching peers of peers:", error);
      return [];
    }

    return data || [];
  } catch (error) {
    console.error("Error in getPeersOfPeers:", error);
    return [];
  }
}

export async function getHistoricalStats(days: number = 30): Promise<any[]> {
  try {
    const { data, error } = await supabase
      .from("network_stats")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(days);

    if (error) {
      console.error("Error fetching historical stats:", error);
      return [];
    }

    return data || [];
  } catch (error) {
    console.error("Error in getHistoricalStats:", error);
    return [];
  }
}
