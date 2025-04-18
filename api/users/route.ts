import { NextRequest, NextResponse } from "next/server";
import { supabase } from "../../lib/supabase";
import { getToken } from "next-auth/jwt";

// GET /api/users - Récupérer tous les utilisateurs (admin seulement)
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

    const { data: users, error } = await supabase.from("users").select(`
        *,
        profile:profiles (
          phone_number,
          bio,
          preferences,
          social_links
        )
      `);

    if (error) {
      throw error;
    }

    return NextResponse.json(users);
  } catch (error) {
    console.error("Erreur lors de la récupération des utilisateurs:", error);
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}

// POST /api/users - Créer un nouvel utilisateur
export async function POST(req: NextRequest) {
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

    const body = await req.json();
    const { email, password, role, first_name, last_name } = body;

    // Vérifier si l'email est déjà utilisé
    const { data: existingUser, error: checkError } = await supabase
      .from("users")
      .select("*")
      .eq("email", email)
      .single();

    if (checkError && checkError.code !== "PGRST116") {
      throw checkError;
    }

    if (existingUser) {
      return NextResponse.json(
        { error: "Cet email est déjà utilisé" },
        { status: 400 }
      );
    }

    // Créer l'utilisateur
    const { data: newUser, error: createError } = await supabase
      .from("users")
      .insert({
        email,
        password,
        role,
        first_name,
        last_name,
      })
      .select()
      .single();

    if (createError) {
      throw createError;
    }

    return NextResponse.json(newUser, { status: 201 });
  } catch (error) {
    console.error("Erreur lors de la création de l'utilisateur:", error);
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}
