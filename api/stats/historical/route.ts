import { NextResponse } from "next/server";
import { getHistoricalStats } from "../../../services/network.service";
import { mockHistoricalData } from "../../../lib/mockData";

export async function GET() {
  try {
    // En développement, utiliser les données simulées
    if (process.env.NODE_ENV === "development") {
      return NextResponse.json(mockHistoricalData);
    }

    const stats = await getHistoricalStats();
    return NextResponse.json(stats);
  } catch (error) {
    console.error("Error fetching historical stats:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
