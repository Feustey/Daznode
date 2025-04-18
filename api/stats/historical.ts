import { NextApiRequest, NextApiResponse } from "next";
import mcpService from "../../lib/mcpService";
import { mockHistoricalData } from "../../lib/mockData";

// Activer le mode développement pour utiliser les données fictives
const devMode = process.env.DEV_MODE === "true";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (devMode) {
    // Utiliser les données fictives en mode développement
    return res.status(200).json(mockHistoricalData);
  }

  try {
    const historicalData = await mcpService.getHistoricalData();
    if (!historicalData) {
      return res.status(404).json({ message: "Historical data not found" });
    }
    return res.status(200).json(historicalData);
  } catch (error) {
    console.error("Error fetching historical data:", error);
    return res.status(500).json({ message: "Internal Server Error" });
  }
}
