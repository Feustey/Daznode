import { NextResponse } from "next/server";

// Configuration de la revalidation
export const revalidate = 300; // Revalider toutes les 5 minutes

// Simuler un appel à l'API MCP
async function fetchDataFromMCP() {
  try {
    // Dans un environnement de production, vous utiliseriez l'API réelle
    // const response = await fetch('http://localhost:8000/api/network/summary');
    // if (response.ok) return await response.json();

    // Données fictives pour la démonstration
    return {
      network_summary: {
        total_nodes: 18934,
        active_nodes: 17500,
        total_channels: 128475,
        active_channels: 115800,
        total_capacity: 523467000000, // en sats
      },
      daily_volume: 450000000, // en sats
      monitored_channels: 52430,
      revenue_growth: 12.5, // pourcentage
    };
  } catch (error) {
    console.error("Error fetching data from MCP:", error);
    throw new Error("Failed to fetch network data");
  }
}

export async function GET() {
  try {
    const stats = await fetchDataFromMCP();

    return NextResponse.json(stats, {
      headers: {
        "Cache-Control": "public, s-maxage=300, stale-while-revalidate=600",
      },
    });
  } catch (error) {
    console.error("Error fetching network stats:", error);
    return NextResponse.json(
      { error: "Failed to fetch network stats" },
      { status: 500 }
    );
  }
}
