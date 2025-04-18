import { NextResponse } from "next/server";

// Marquer cette route comme dynamique
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const query = searchParams.get("q") || "";

    if (!query) {
      return NextResponse.json([]);
    }

    // Générer des données fictives pour les résultats de recherche
    // Dans une implémentation réelle, cela filtre en fonction de la requête
    const queryLower = query.toLowerCase();

    // Créer quelques nœuds fictifs basés sur la requête
    const mockSearchResults = Array.from({ length: 5 }, (_, i) => ({
      rank: i + 1,
      name: `${query} Node ${i + 1}`,
      channels: Math.floor(Math.random() * 100) + 10,
      capacity: Math.floor(Math.random() * 1000000) + 50000,
      pubkey: `pubkey_${queryLower}_${i + 1}`,
      lastSeen: new Date().toISOString(),
      uptime: Math.random() * 100,
    }));

    return NextResponse.json(mockSearchResults);
  } catch (error) {
    console.error("Error searching nodes:", error);
    return NextResponse.json(
      { error: "Failed to search nodes" },
      { status: 500 }
    );
  }
}
