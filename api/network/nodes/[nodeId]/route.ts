import { NextResponse } from "next/server";

export async function GET(
  request: Request,
  { params }: { params: { nodeId: string } }
) {
  try {
    const nodeId = params.nodeId;

    // Données fictives pour la démonstration
    const mockNode = {
      rank: parseInt(nodeId.replace("pubkey_", "")) || 1,
      name: `Node ${nodeId}`,
      channels: Math.floor(Math.random() * 100) + 10,
      capacity: Math.floor(Math.random() * 1000000) + 50000,
      pubkey: nodeId,
      lastSeen: new Date().toISOString(),
      uptime: Math.random() * 100,
      // Données supplémentaires détaillées
      nodeDetails: {
        location: "Frankfurt, Germany",
        version: "v0.15.1-beta",
        color: "#3399ff",
        platform: "Linux 5.15.0",
        created: new Date(
          Date.now() - Math.random() * 31536000000
        ).toISOString(),
        feeRate: Math.floor(Math.random() * 1000),
        maxHTLC: "0.1 BTC",
        minHTLC: "0.00001 BTC",
      },
    };

    return NextResponse.json(mockNode);
  } catch (error) {
    console.error(`Error fetching node details for ${params.nodeId}:`, error);
    return NextResponse.json(
      { error: "Failed to fetch node details" },
      { status: 500 }
    );
  }
}
