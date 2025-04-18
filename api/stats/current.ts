import { NextApiRequest, NextApiResponse } from "next";
import { NextResponse } from "next/server";
import mcpService from "../../lib/mcpService";
import { mockNetworkStats } from "../../lib/mockData";

// Activer le mode développement pour utiliser les données fictives
const devMode = process.env.DEV_MODE === "true";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (devMode) {
    // Utiliser les données fictives en mode développement
    return res.status(200).json(mockNetworkStats);
    // Remarque : L'utilisation de res.status().json() est typique pour les API Routes Next.js traditionnelles.
    // Si c'était une Route Handler (dans le dossier app), on utiliserait NextResponse.json().
  }

  try {
    const stats = await mcpService.getCurrentStats();
    if (!stats) {
      return res.status(404).json({ message: "Stats not found" });
    }
    return res.status(200).json(stats);
  } catch (error) {
    console.error("Error fetching current stats:", error);
    return res.status(500).json({ message: "Internal Server Error" });
  }
}
