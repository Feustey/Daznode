import { NextResponse } from "next/server";

export async function GET(
  request: Request,
  { params }: { params: { nodeId: string } }
) {
  try {
    const nodeId = params.nodeId;

    // Générer des données fictives pour les canaux
    const channelCount = Math.floor(Math.random() * 30) + 5;

    const mockChannels = Array.from({ length: channelCount }, (_, i) => ({
      id: `chan_${i + 1}_${nodeId}`,
      capacity: Math.floor(Math.random() * 10000000) + 100000,
      localBalance: Math.floor(Math.random() * 5000000) + 50000,
      remoteBalance: Math.floor(Math.random() * 5000000) + 50000,
      active: Math.random() > 0.2,
      remotePubkey: `remote_pubkey_${i + 1}`,
      remoteName: `Remote Node ${i + 1}`,
      channelPoint: `${Math.random().toString(16).substring(2)}:${i}`,
      age: Math.floor(Math.random() * 1000) + 1,
      feeBaseMsat: Math.floor(Math.random() * 1000),
      feeRateMilliMsat: Math.floor(Math.random() * 5000),
      lastUpdate: new Date(
        Date.now() - Math.random() * 2592000000
      ).toISOString(),
    }));

    return NextResponse.json(mockChannels);
  } catch (error) {
    console.error(`Error fetching channels for node ${params.nodeId}:`, error);
    return NextResponse.json(
      { error: "Failed to fetch node channels" },
      { status: 500 }
    );
  }
}
