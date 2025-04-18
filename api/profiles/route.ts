import { NextRequest, NextResponse } from "next/server";
import { supabase } from "../../lib/supabase";
import { getToken } from "next-auth/jwt";

// GET /api/profiles - Récupérer tous les profils (admin seulement)
export async function GET(req: NextRequest) {
  try {
    const token = await getToken({ req });
    if (!token) {
      return NextResponse.json(
        { error: "Vous devez être connecté" },
        { status: 401 }
      );
    }

    // Vérifier si l'utilisateur est admin
    if (token.role !== "admin") {
      return NextResponse.json(
        { error: "Accès non autorisé" },
        { status: 403 }
      );
    }

    const { data: profiles, error } = await supabase.from("profiles").select(`
        *,
        user:users (
          first_name,
          last_name,
          email
        )
      `);

    if (error) {
      throw error;
    }

    return NextResponse.json(profiles);
  } catch (error) {
    console.error("Erreur lors de la récupération des profils:", error);
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}

// POST /api/profiles - Créer un nouveau profil
export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { userId, phoneNumber, bio, preferences, socialLinks } = body;

    // Vérifier si un profil existe déjà pour cet utilisateur
    const { data: existingProfile, error: checkError } = await supabase
      .from("profiles")
      .select("*")
      .eq("user_id", userId)
      .single();

    if (checkError && checkError.code !== "PGRST116") {
      throw checkError;
    }

    if (existingProfile) {
      return NextResponse.json(
        { error: "Un profil existe déjà pour cet utilisateur" },
        { status: 400 }
      );
    }

    // Créer le nouveau profil
    const { data: newProfile, error: createError } = await supabase
      .from("profiles")
      .insert({
        user_id: userId,
        phone_number: phoneNumber,
        bio,
        preferences,
        social_links: socialLinks,
      })
      .select()
      .single();

    if (createError) {
      throw createError;
    }

    return NextResponse.json(newProfile, { status: 201 });
  } catch (error) {
    console.error("Erreur lors de la création du profil:", error);
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}
