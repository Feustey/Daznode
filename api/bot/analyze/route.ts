import mcpService from "../../../lib/mcpService.edge";
import { NextResponse } from "next/server";
import { errorResponse, successResponse } from "../../edge-config";

export const runtime = "edge";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const { question } = await request.json();
    const nodePubkey = process.env.NODE_PUBKEY;

    if (!nodePubkey) {
      throw new Error(
        "NODE_PUBKEY non défini dans les variables d'environnement"
      );
    }

    // Récupérer toutes les données nécessaires
    const [nodeInfo, networkMetrics, peersOfPeers, recommendations] =
      await Promise.all([
        mcpService.getNodeInfo(nodePubkey),
        mcpService.getNetworkSummary(),
        mcpService.getPeersOfPeers(nodePubkey),
        mcpService.analyzeQuestion(question),
      ]);

    return successResponse({
      status: "success",
      nodeInfo,
      networkMetrics,
      peersOfPeers,
      recommendations,
    });
  } catch (error) {
    console.error("Erreur lors de l'analyse:", error);
    return errorResponse("Erreur lors de l'analyse de la question");
  }
}
