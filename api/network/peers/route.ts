import { NextResponse } from "next/server";

export async function GET() {
  try {
    // Logique pour récupérer les pairs du réseau
    const peers = [
      // Exemple de données de pairs
      { id: "peer1", address: "192.168.1.1", status: "connected" },
      { id: "peer2", address: "192.168.1.2", status: "disconnected" },
    ];

    return NextResponse.json({ success: true, peers });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: "Erreur lors de la récupération des pairs" },
      { status: 500 }
    );
  }
}
