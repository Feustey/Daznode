import { NextResponse } from "next/server";
import { getSession } from "../../../lib/edge-auth";
import { type NextRequest } from "next/server";

// Marquer cette route comme dynamique
export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  try {
    const session = await getSession(request);
    if (!session) {
      return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
    }
    return NextResponse.json(session);
  } catch (error) {
    console.error("Error checking session:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
