import { NextRequest, NextResponse } from "next/server";
import { supabase } from "../../../lib/supabase";
import { getToken } from "next-auth/jwt";

export const dynamic = "force-dynamic";

// GET /api/user/profile - Récupérer le profil de l'utilisateur connecté
export async function GET(req: NextRequest) {
  try {
    const token = await getToken({ req });
    if (!token) {
      return NextResponse.json(
        { error: "Vous devez être connecté" },
        { status: 401 }
      );
    }

    const { data: profile, error } = await supabase
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
      .eq("user_id", token.sub)
      .single();

    if (error) {
      throw error;
    }

    if (!profile) {
      return NextResponse.json({ error: "Profil non trouvé" }, { status: 404 });
    }

    return NextResponse.json(profile);
  } catch (error) {
    console.error("Erreur lors de la récupération du profil:", error);
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}

// PUT /api/user/profile - Mettre à jour le profil de l'utilisateur connecté
export async function PUT(req: NextRequest) {
  try {
    const token = await getToken({ req });
    if (!token) {
      return NextResponse.json(
        { error: "Vous devez être connecté" },
        { status: 401 }
      );
    }

    const body = await req.json();
    const { phone_number, bio, preferences, social_links } = body;

    // Vérifier si le profil existe
    const { data: existingProfile, error: checkError } = await supabase
      .from("profiles")
      .select("*")
      .eq("user_id", token.sub)
      .single();

    if (checkError && checkError.code !== "PGRST116") {
      throw checkError;
    }

    if (!existingProfile) {
      // Créer le profil s'il n'existe pas
      const { data: newProfile, error: createError } = await supabase
        .from("profiles")
        .insert({
          user_id: token.sub,
          phone_number,
          bio,
          preferences,
          social_links,
        })
        .select()
        .single();

      if (createError) {
        throw createError;
      }

      return NextResponse.json(newProfile);
    }

    // Mettre à jour le profil existant
    const { data: updatedProfile, error: updateError } = await supabase
      .from("profiles")
      .update({
        phone_number,
        bio,
        preferences,
        social_links,
      })
      .eq("user_id", token.sub)
      .select()
      .single();

    if (updateError) {
      throw updateError;
    }

    return NextResponse.json(updatedProfile);
  } catch (error) {
    console.error("Erreur lors de la mise à jour du profil:", error);
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}
