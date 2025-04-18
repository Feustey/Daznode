import { NextResponse } from "next/server";
import { basicMcpService } from "../../services/basicMcpService";
import { mockCentralities } from "../../lib/mockData";

// Activer le mode dynamique pour éviter le cache
export const dynamic = "force-dynamic";

// Activer le mode développement pour utiliser les données fictives
const USE_MOCK_DATA =
  process.env.NODE_ENV === "development" &&
  process.env.USE_MOCK_DATA === "true";

// Données fictives pour le développement si elles ne sont pas déjà définies dans mockData.ts
const mockCentralitiesDefault = {
  betweenness: Array.from({ length: 20 }, (_, i) => ({
    pubkey: `02${Math.random().toString(16).substring(2, 30)}`,
    value: Math.random() * 0.1,
    rank: i + 1,
  })),
  eigenvector: Array.from({ length: 20 }, (_, i) => ({
    pubkey: `03${Math.random().toString(16).substring(2, 30)}`,
    value: Math.random() * 0.1,
    rank: i + 1,
  })),
  closeness: Array.from({ length: 20 }, (_, i) => ({
    pubkey: `03${Math.random().toString(16).substring(2, 30)}`,
    value: Math.random() * 0.1,
    rank: i + 1,
  })),
  weighted_betweenness: Array.from({ length: 20 }, (_, i) => ({
    pubkey: `02${Math.random().toString(16).substring(2, 30)}`,
    value: Math.random() * 0.1,
    rank: i + 1,
  })),
  weighted_eigenvector: Array.from({ length: 20 }, (_, i) => ({
    pubkey: `03${Math.random().toString(16).substring(2, 30)}`,
    value: Math.random() * 0.1,
    rank: i + 1,
  })),
  weighted_closeness: Array.from({ length: 20 }, (_, i) => ({
    pubkey: `03${Math.random().toString(16).substring(2, 30)}`,
    value: Math.random() * 0.1,
    rank: i + 1,
  })),
  last_update: new Date().toISOString(),
};

export async function GET() {
  try {
    // Si l'API MCP n'est pas disponible et que nous sommes en mode développement, utilisez des données fictives
    const isMcpAvailable = await basicMcpService.testConnection();

    if (!isMcpAvailable && USE_MOCK_DATA) {
      console.log(
        "API centralities route: utilisation des données fictives (mode développement, MCP indisponible)"
      );
      return NextResponse.json(mockCentralities || mockCentralitiesDefault);
    }

    // Sinon, récupérer les données réelles
    const centralities = await basicMcpService.getTopCentralities();
    console.log(
      "API centralities route: données de centralité récupérées avec succès"
    );
    return NextResponse.json(centralities);
  } catch (error) {
    console.error("Error fetching centralities:", error);

    // Si mode développement, retournez des données fictives
    if (USE_MOCK_DATA) {
      console.log(
        "API centralities route: utilisation des données fictives (mode développement, erreur)"
      );
      return NextResponse.json(mockCentralities || mockCentralitiesDefault);
    }

    // Sinon, retournez une erreur
    return new NextResponse(
      JSON.stringify({
        message: "Erreur lors de la récupération des données de centralité",
        error: error instanceof Error ? error.message : String(error),
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}
