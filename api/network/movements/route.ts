import { NextResponse } from "next/server";

// Marquer cette route comme dynamique
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const period = searchParams.get("period") || "daily";

    // Générer des données fictives pour les mouvements du réseau
    const mockMovements = Array.from({ length: 15 }, (_, i) => {
      const isPositive = Math.random() > 0.3;
      const capacityChange = Math.floor(Math.random() * 500000) + 10000;
      const channelsChange = Math.floor(Math.random() * 5) + 1;

      return {
        id: `movement_${i + 1}`,
        name: `Node ${i + 1}`,
        capacity: `${Math.floor(Math.random() * 5000000) + 500000}`,
        capacityChange: `${isPositive ? "+" : "-"}${capacityChange}`,
        channels: `${Math.floor(Math.random() * 100) + 10}`,
        channelsChange: `${isPositive ? "+" : "-"}${channelsChange}`,
        timestamp: new Date(
          Date.now() - Math.random() * 86400000
        ).toISOString(),
      };
    });

    // Trier par valeur absolue de changement de capacité décroissante
    mockMovements.sort((a, b) => {
      const aChange = parseInt(a.capacityChange.replace(/[+\-]/g, ""));
      const bChange = parseInt(b.capacityChange.replace(/[+\-]/g, ""));
      return bChange - aChange;
    });

    return NextResponse.json(mockMovements);
  } catch (error) {
    console.error("Error fetching network movements:", error);
    return NextResponse.json(
      { error: "Failed to fetch network movements" },
      { status: 500 }
    );
  }
}
