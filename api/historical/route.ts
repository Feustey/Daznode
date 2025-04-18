import { NextResponse } from "next/server";
import { basicMcpService } from "../../services/basicMcpService";
import { mockHistoricalData } from "../../lib/mockData";

// Activer le mode dynamique pour éviter le cache
export const dynamic = "force-dynamic";

// Activer le mode développement pour utiliser les données fictives
const USE_MOCK_DATA =
  process.env.NODE_ENV === "development" &&
  process.env.USE_MOCK_DATA === "true";

export async function GET() {
  try {
    // Si l'API MCP n'est pas disponible et que nous sommes en mode développement, utilisez des données fictives
    const isMcpAvailable = await basicMcpService.testConnection();

    if (!isMcpAvailable && USE_MOCK_DATA) {
      console.log(
        "API historical route: utilisation des données fictives (mode développement, MCP indisponible)"
      );
      return NextResponse.json(mockHistoricalData);
    }

    // Sinon, récupérer les données réelles
    const historicalData = await basicMcpService.getLimitedHistoricalData();
    console.log(
      "API historical route: données historiques récupérées avec succès"
    );
    return NextResponse.json(historicalData);
  } catch (error) {
    console.error("Error fetching historical data:", error);

    // Si mode développement, retournez des données fictives
    if (USE_MOCK_DATA) {
      console.log(
        "API historical route: utilisation des données fictives (mode développement, erreur)"
      );
      return NextResponse.json(mockHistoricalData);
    }

    // Sinon, retournez une erreur
    return new NextResponse(
      JSON.stringify({
        message: "Erreur lors de la récupération des données historiques",
        error: error instanceof Error ? error.message : String(error),
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}
