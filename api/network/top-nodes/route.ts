import { NextResponse } from "next/server";

// Marquer cette route comme dynamique
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const period = searchParams.get("period") || "daily";

    // Générer des données fictives pour les top nœuds
    const mockTopNodes = Array.from({ length: 10 }, (_, i) => ({
      rank: i + 1,
      name: `Top Node ${i + 1}`,
      channels: Math.floor(Math.random() * 200) + 50,
      capacity: Math.floor(Math.random() * 5000000) + 1000000,
      pubkey: `pubkey_top_${i + 1}`,
      lastSeen: new Date().toISOString(),
      uptime: 99 - i * 0.5,
      growth: {
        capacity: Math.floor(Math.random() * 1000000) + 10000,
        channels: Math.floor(Math.random() * 10) + 1,
      },
    }));

    // Trier par capacité décroissante
    mockTopNodes.sort((a, b) => b.capacity - a.capacity);

    return NextResponse.json(mockTopNodes);
  } catch (error) {
    console.error("Error fetching top nodes:", error);
    return NextResponse.json(
      { error: "Failed to fetch top nodes" },
      { status: 500 }
    );
  }
}
