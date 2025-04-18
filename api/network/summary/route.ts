import { NextResponse } from "next/server";
import { supabase } from "../../../lib/supabase";

// Spécifier que nous utilisons le runtime Node.js et non Edge
export const runtime = "nodejs";

export async function GET() {
  try {
    const { data: summary, error } = await supabase
      .from("network_summary")
      .select("*")
      .single();

    if (error) {
      throw error;
    }

    return NextResponse.json(summary);
  } catch (error) {
    console.error("Erreur lors de la récupération du résumé du réseau:", error);
    return NextResponse.json(
      { error: "Erreur lors de la récupération du résumé du réseau" },
      { status: 500 }
    );
  }
}
