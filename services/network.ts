const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface NetworkStats {
  totalNodes: number;
  totalChannels: number;
  totalCapacity: number;
  capacityHistory: Array<{ date: string; value: number }>;
  nodesByCountry: Array<{ country: string; count: number }>;
  lastUpdate?: string;
}

// Convertit les sats en BTC
const satsToBtc = (sats: number) => sats / 100000000;

// Formate la date pour l'affichage
const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

export async function getNetworkStats(): Promise<NetworkStats> {
  try {
    const response = await fetch(`${API_BASE_URL}/network/stats`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();

    // Conversion des sats en BTC pour la capacité
    const totalCapacity = satsToBtc(data.total_capacity || 0);

    // Formatage de l'historique de capacité
    const capacityHistory =
      data.capacity_history?.map((item: any) => ({
        date: formatDate(item.date),
        value: satsToBtc(item.value),
      })) || [];

    // Tri des pays par nombre de nœuds décroissant
    const nodesByCountry = (
      data.nodes_by_country?.map((item: any) => ({
        country: item.country,
        count: item.count,
      })) || []
    ).sort((a, b) => b.count - a.count);

    return {
      totalNodes: data.total_nodes || 0,
      totalChannels: data.total_channels || 0,
      totalCapacity,
      capacityHistory,
      nodesByCountry,
      lastUpdate: new Date().toISOString(),
    };
  } catch (error) {
    console.error("Error fetching network stats:", error);
    throw error;
  }
}

// Fonction pour récupérer les données historiques avec une période spécifique
export async function getHistoricalData(
  period: "1d" | "1w" | "1m" | "1y" = "1m"
): Promise<Array<{ date: string; value: number }>> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/network/history?period=${period}`
    );
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();

    return data.map((item: any) => ({
      date: formatDate(item.date),
      value: satsToBtc(item.value),
    }));
  } catch (error) {
    console.error("Error fetching historical data:", error);
    throw error;
  }
}

// Fonction pour récupérer les détails d'un pays spécifique
export async function getCountryDetails(countryCode: string): Promise<{
  nodes: number;
  channels: number;
  capacity: number;
}> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/network/country/${countryCode}`
    );
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();

    return {
      nodes: data.nodes || 0,
      channels: data.channels || 0,
      capacity: satsToBtc(data.capacity || 0),
    };
  } catch (error) {
    console.error("Error fetching country details:", error);
    throw error;
  }
}
