import { NextResponse } from "next/server";
import { getCurrentStats } from "../../../services/network.service";
import {
  successResponse,
  errorResponse,
  HttpStatus,
} from "../../../lib/api/responses";
import { mockNetworkStats } from "../../../lib/mockData";

// Définir qu'on n'utilise pas Edge Runtime
export const runtime = "nodejs";

// Activer le mode développement pour utiliser les données fictives
const USE_MOCK_DATA = process.env.NODE_ENV === "development";

export const GET = async () => {
  try {
    // En développement, utiliser les données simulées
    if (USE_MOCK_DATA) {
      return successResponse(mockNetworkStats);
    }

    const stats = await getCurrentStats();
    console.log(
      "API stats/current route: statistiques actuelles récupérées avec succès"
    );

    return successResponse(stats);
  } catch (error) {
    console.error("Error fetching current stats:", error);
    return errorResponse("Internal server error", {
      status: HttpStatus.INTERNAL_SERVER_ERROR,
    });
  }
};

// Définir une stratégie de mise en cache appropriée
export const revalidate = 600; // Revalider toutes les 10 minutes
