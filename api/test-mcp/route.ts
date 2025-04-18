import { NextResponse } from "next/server";
import { dynamic } from "../../api/config";

export const runtime = "nodejs";
export { dynamic };

export async function GET() {
  const API_URL = "http://192.168.0.21:8000";

  try {
    const response = await fetch(`${API_URL}/status`);

    if (response.ok) {
      return NextResponse.json({
        status: "success",
        message: "Connexion à l'API MCP réussie",
      });
    } else {
      return NextResponse.json(
        {
          status: "error",
          message: `Erreur de connexion à l'API MCP: ${response.status} ${response.statusText}`,
        },
        { status: response.status }
      );
    }
  } catch (error) {
    console.error("Erreur lors du test de connexion:", error);
    return NextResponse.json(
      {
        status: "error",
        message: "Erreur lors du test de connexion à l'API MCP",
        error: error instanceof Error ? error.message : String(error),
      },
      { status: 500 }
    );
  }
}
