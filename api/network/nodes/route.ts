import { NextResponse } from "next/server";
import { NetworkNode } from "../../../types/network";

// Fonction pour générer une couleur aléatoire au format hexadécimal
const randomColor = () => {
  return (
    "#" +
    Math.floor(Math.random() * 16777215)
      .toString(16)
      .padStart(6, "0")
  );
};

// Données fictives pour la démonstration
const mockNodes: NetworkNode[] = Array.from({ length: 50 }, (_, i) => ({
  publicKey: `0${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`,
  alias: `⚡ Node ${i + 1} ${["🔥", "⚡️", "🚀", "💫"][Math.floor(Math.random() * 4)]}`,
  color: randomColor(),
  addresses: [
    `${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}:9735`,
  ],
  lastUpdate: new Date(
    Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000
  ),
  capacity: Math.floor(Math.random() * 10000000) + 1000000,
  channelCount: Math.floor(Math.random() * 100) + 10,
  avgChannelSize: Math.floor(Math.random() * 1000000) + 100000,
  city: ["Paris", "New York", "Tokyo", "London", "Berlin"][
    Math.floor(Math.random() * 5)
  ],
  country: ["FR", "US", "JP", "GB", "DE"][Math.floor(Math.random() * 5)],
  isp: ["OVH", "AWS", "Digital Ocean", "Google Cloud", "Azure"][
    Math.floor(Math.random() * 5)
  ],
  platform: ["LND", "c-lightning", "eclair", "btcd"][
    Math.floor(Math.random() * 4)
  ],
  betweennessRank: Math.floor(Math.random() * 1000) + 1,
  eigenvectorRank: Math.floor(Math.random() * 1000) + 1,
  closenessRank: Math.floor(Math.random() * 1000) + 1,
  avgFeeRate: Math.floor(Math.random() * 500) + 1,
  uptime: Math.random() * 100,
  rank: Math.floor(Math.random() * 50) + 1,
}));

export async function GET() {
  try {
    // Ici vous pourriez implémenter la vraie logique pour récupérer les nœuds
    // Par exemple, requête à une base de données ou appel à un service externe
    return NextResponse.json(mockNodes);
  } catch (error) {
    console.error("Error fetching network nodes:", error);
    return NextResponse.json(
      { error: "Failed to fetch network nodes" },
      { status: 500 }
    );
  }
}
