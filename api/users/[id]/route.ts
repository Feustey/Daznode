import { NextRequest, NextResponse } from "next/server";
import { supabase } from "../../../lib/supabase";
import { getToken } from "next-auth/jwt";

// GET /api/users/[id] - Récupérer un utilisateur spécifique
export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const token = await getToken({ req });
    if (!token) {
      return NextResponse.json(
        { error: "Vous devez être connecté" },
        { status: 401 }
      );
    }

    // Vérifier si l'utilisateur est admin ou s'il s'agit de son propre compte
    if (token.role !== "admin" && token.sub !== params.id) {
      return NextResponse.json(
        { error: "Accès non autorisé" },
        { status: 403 }
      );
    }

    const { data: user, error } = await supabase
      .from("users")
      .select(
        `
        *,
        profile:profiles (
          phone_number,
          bio,
          preferences,
          social_links
        )
      `
      )
      .eq("id", params.id)
      .single();

    if (error) {
      throw error;
    }

    if (!user) {
      return NextResponse.json(
        { error: "Utilisateur non trouvé" },
        { status: 404 }
      );
    }

    return NextResponse.json(user);
  } catch (error) {
    console.error("Erreur lors de la récupération de l'utilisateur:", error);
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}

// PUT /api/users/[id] - Mettre à jour un utilisateur
export async function PUT(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const token = await getToken({ req });
    if (!token) {
      return NextResponse.json(
        { error: "Vous devez être connecté" },
        { status: 401 }
      );
    }

    // Vérifier si l'utilisateur est admin ou s'il s'agit de son propre compte
    if (token.role !== "admin" && token.sub !== params.id) {
      return NextResponse.json(
        { error: "Accès non autorisé" },
        { status: 403 }
      );
    }

    const body = await req.json();
    const { email, role, first_name, last_name } = body;

    // Vérifier si l'utilisateur existe
    const { data: existingUser, error: checkError } = await supabase
      .from("users")
      .select("*")
      .eq("id", params.id)
      .single();

    if (checkError) {
      throw checkError;
    }

    if (!existingUser) {
      return NextResponse.json(
        { error: "Utilisateur non trouvé" },
        { status: 404 }
      );
    }

    // Vérifier si l'email est déjà utilisé par un autre utilisateur
    if (email && email !== existingUser.email) {
      const { data: emailUser, error: emailCheckError } = await supabase
        .from("users")
        .select("*")
        .eq("email", email)
        .neq("id", params.id)
        .single();

      if (emailCheckError && emailCheckError.code !== "PGRST116") {
        throw emailCheckError;
      }

      if (emailUser) {
        return NextResponse.json(
          { error: "Cet email est déjà utilisé" },
          { status: 400 }
        );
      }
    }

    // Mettre à jour l'utilisateur
    const { data: updatedUser, error: updateError } = await supabase
      .from("users")
      .update({
        email,
        role,
        first_name,
        last_name,
      })
      .eq("id", params.id)
      .select()
      .single();

    if (updateError) {
      throw updateError;
    }

    return NextResponse.json(updatedUser);
  } catch (error) {
    console.error("Erreur lors de la mise à jour de l'utilisateur:", error);
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}

// DELETE /api/users/[id] - Supprimer un utilisateur
export async function DELETE(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
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

    // Vérifier si l'utilisateur existe
    const { data: user, error: checkError } = await supabase
      .from("users")
      .select("*")
      .eq("id", params.id)
      .single();

    if (checkError) {
      throw checkError;
    }

    if (!user) {
      return NextResponse.json(
        { error: "Utilisateur non trouvé" },
        { status: 404 }
      );
    }

    // Supprimer l'utilisateur
    const { error: deleteError } = await supabase
      .from("users")
      .delete()
      .eq("id", params.id);

    if (deleteError) {
      throw deleteError;
    }

    return NextResponse.json(
      { message: "Utilisateur supprimé avec succès" },
      { status: 200 }
    );
  } catch (error) {
    console.error("Erreur lors de la suppression de l'utilisateur:", error);
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}
