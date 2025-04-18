import { NextRequest, NextResponse } from "next/server";
import { premiumMcpService } from "../../../services/premiumMcpService";
import { auth } from "../../../lib/auth";
import { authOptions } from "../../../lib/auth-options";

// Activer le mode dynamique pour éviter le cache
export const dynamic = "force-dynamic";

// Middleware pour vérifier l'accès premium
async function checkPremiumAccess(request: NextRequest, nodeId: string) {
  const session = await auth();

  if (!session || !session.user?.id) {
    return {
      hasAccess: false,
      error: "Authentification requise",
      status: 401,
    };
  }

  const userId = session.user.id;

  try {
    // Vérifier si l'utilisateur a un abonnement ou un accès one-shot
    const hasSubscription = await premiumMcpService.checkSubscription(userId);
    const hasOneTimeAccess = await premiumMcpService.checkOneTimeAccess(
      userId,
      nodeId
    );

    if (!hasSubscription && !hasOneTimeAccess) {
      return {
        hasAccess: false,
        error:
          "Cette fonctionnalité nécessite un abonnement premium ou un achat one-shot",
        status: 403,
      };
    }

    return { hasAccess: true, userId };
  } catch (error) {
    console.error("Erreur lors de la vérification de l'accès premium:", error);
    return {
      hasAccess: false,
      error: "Erreur de vérification d'accès",
      status: 500,
    };
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { nodeId: string } }
) {
  const { nodeId } = params;

  // Vérifier l'accès
  const accessCheck = await checkPremiumAccess(request, nodeId);

  if (!accessCheck.hasAccess) {
    return NextResponse.json(
      { error: accessCheck.error },
      { status: accessCheck.status }
    );
  }

  try {
    const optimizationResult = await premiumMcpService.optimizeNode(
      nodeId,
      accessCheck.userId
    );

    return NextResponse.json(optimizationResult);
  } catch (error) {
    console.error(`Erreur lors de l'optimisation du nœud ${nodeId}:`, error);

    return NextResponse.json(
      {
        error: "Erreur lors de l'optimisation du nœud",
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 500 }
    );
  }
}
