import { NextResponse } from "next/server";
import { supabase } from "../../lib/supabase";

// Spécifier que nous utilisons le runtime Node.js et non Edge
export const runtime = "nodejs";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    // Récupérer les statistiques depuis Supabase
    const { data: stats, error } = await supabase
      .from("stats")
      .select("*")
      .single();

    if (error) {
      throw error;
    }

    return NextResponse.json(stats);
  } catch (error) {
    console.error("Erreur lors de la récupération des statistiques:", error);
    return NextResponse.json(
      { error: "Erreur lors de la récupération des statistiques" },
      { status: 500 }
    );
  }
}
