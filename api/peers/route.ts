import { getPeersOfPeers } from "../../services/network.service";
import {
  successResponse,
  errorResponse,
  HttpStatus,
} from "../../lib/api/responses";

// Configuration de la revalidation
export const revalidate = 300; // Revalider toutes les 5 minutes

export async function GET(request: Request) {
  try {
    const url = new URL(request.url);
    const nodePubkey = url.searchParams.get("nodePubkey");

    if (!nodePubkey) {
      return errorResponse("Le paramètre nodePubkey est requis", {
        status: HttpStatus.BAD_REQUEST,
      });
    }

    const peersData = await getPeersOfPeers(nodePubkey);
    return successResponse(peersData, {
      headers: {
        "Cache-Control": "public, s-maxage=300, stale-while-revalidate=600",
      },
    });
  } catch (error) {
    console.error("Error fetching peers:", error);
    return errorResponse("Erreur lors de la récupération des pairs", {
      status: HttpStatus.INTERNAL_SERVER_ERROR,
    });
  }
}
