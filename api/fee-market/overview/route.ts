import { NextResponse } from "next/server";
import { basicMcpService } from "../../../services/basicMcpService";

// Activer le mode dynamique pour éviter le cache
export const dynamic = "force-dynamic";

// Activer le mode développement pour utiliser les données fictives
const USE_MOCK_DATA =
  process.env.NODE_ENV === "development" &&
  process.env.USE_MOCK_DATA === "true";

// Données fictives pour le marché des frais
const mockFeeMarketOverview = {
  average: {
    base_fee_msat: 1000,
    fee_rate_ppm: 500,
  },
  distribution: {
    ranges: [
      { min: 0, max: 100, count: 5000 },
      { min: 100, max: 300, count: 15000 },
      { min: 300, max: 500, count: 25000 },
      { min: 500, max: 1000, count: 18000 },
      { min: 1000, max: 2000, count: 10000 },
      { min: 2000, max: 5000, count: 5000 },
      { min: 5000, max: Number.MAX_SAFE_INTEGER, count: 2000 },
    ],
    percentiles: {
      p10: 150,
      p25: 250,
      p50: 400,
      p75: 800,
      p90: 1500,
    },
  },
  timestamp: new Date().toISOString(),
};

export async function GET() {
  try {
    // Si l'API MCP n'est pas disponible et que nous sommes en mode développement, utilisez des données fictives
    const isMcpAvailable = await basicMcpService.testConnection();

    if (!isMcpAvailable && USE_MOCK_DATA) {
      console.log(
        "API fee-market/overview route: utilisation des données fictives (mode développement, MCP indisponible)"
      );
      return NextResponse.json(mockFeeMarketOverview);
    }

    // Sinon, récupérer les données réelles
    const feeMarketData = await basicMcpService.getFeeMarketOverview();
    console.log(
      "API fee-market/overview route: données du marché des frais récupérées avec succès"
    );
    return NextResponse.json(feeMarketData);
  } catch (error) {
    console.error("Error fetching fee market overview:", error);

    // Si mode développement, retournez des données fictives
    if (USE_MOCK_DATA) {
      console.log(
        "API fee-market/overview route: utilisation des données fictives (mode développement, erreur)"
      );
      return NextResponse.json(mockFeeMarketOverview);
    }

    // Sinon, retournez une erreur
    return new NextResponse(
      JSON.stringify({
        message:
          "Erreur lors de la récupération des données du marché des frais",
        error: error instanceof Error ? error.message : String(error),
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}
