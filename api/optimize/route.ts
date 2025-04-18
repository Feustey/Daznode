import { NextResponse } from "next/server";
import mcpService from "../../lib/mcpService";

export async function GET() {
  try {
    const pubkey = process.env.NODE_PUBKEY;

    if (!pubkey) {
      return NextResponse.json(
        { error: "La pubkey du nœud n'est pas configurée" },
        { status: 500 }
      );
    }

    const optimizationResult = await mcpService.optimizeNode(pubkey);
    const nodeInfo = await mcpService.getNodeInfo(pubkey);

    return NextResponse.json({
      ...optimizationResult,
      nodeInfo,
    });
  } catch (error) {
    console.error("Erreur lors de la récupération des données:", error);
    return NextResponse.json(
      { error: "Erreur lors de la récupération des données" },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { pubkey } = body;

    if (!pubkey) {
      return NextResponse.json(
        { error: "La pubkey du nœud est requise" },
        { status: 400 }
      );
    }

    const optimizationResult = await mcpService.optimizeNode(pubkey);
    const nodeInfo = await mcpService.getNodeInfo(pubkey);

    return NextResponse.json({
      ...optimizationResult,
      nodeInfo,
    });
  } catch (error) {
    console.error("Erreur lors de l'optimisation du nœud:", error);
    return NextResponse.json(
      { error: "Erreur lors de l'optimisation du nœud" },
      { status: 500 }
    );
  }
}
