import { NextResponse } from "next/server";
import { supabase } from "../../lib/supabase";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const type = url.searchParams.get("type");

  try {
    let data = {};

    switch (type) {
      case "stats":
        // Récupérer les statistiques depuis Supabase
        const { data: stats, error: statsError } = await supabase
          .from("stats")
          .select("*")
          .single();

        if (statsError) {
          throw statsError;
        }

        data = { stats };
        break;

      case "profile":
        // Récupérer les données de profil
        const userId = url.searchParams.get("userId");
        if (!userId) {
          return NextResponse.json(
            { error: "ID utilisateur requis" },
            { status: 400 }
          );
        }

        const { data: profile, error: profileError } = await supabase
          .from("profiles")
          .select(
            `
            *,
            user:users (
              first_name,
              last_name,
              email
            )
          `
          )
          .eq("user_id", userId)
          .single();

        if (profileError) {
          throw profileError;
        }

        data = { profile };
        break;

      case "nodes":
        // Récupérer la liste des nœuds
        const { data: nodes, error: nodesError } = await supabase
          .from("nodes")
          .select("*");

        if (nodesError) {
          throw nodesError;
        }

        data = { nodes };
        break;

      default:
        return NextResponse.json(
          { error: "Type de données non spécifié" },
          { status: 400 }
        );
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error("Erreur lors de la récupération des données:", error);
    return NextResponse.json(
      { error: "Erreur lors de la récupération des données" },
      { status: 500 }
    );
  }
}
