import { NextRequest, NextResponse } from "next/server";
import { supabase } from "../../../lib/supabase";

export async function PUT(req: NextRequest) {
  try {
    const body = await req.json();
    const { userId, name, email } = body;

    if (!userId) {
      return NextResponse.json(
        { error: "ID utilisateur requis" },
        { status: 400 }
      );
    }

    // Vérifier si l'utilisateur existe
    const { data: user, error: getUserError } = await supabase
      .from("users")
      .select("*")
      .eq("id", userId)
      .single();

    if (getUserError || !user) {
      return NextResponse.json(
        { error: "Utilisateur non trouvé" },
        { status: 404 }
      );
    }

    // Vérifier si l'email est déjà utilisé par un autre utilisateur
    if (email && email !== user.email) {
      const { data: existingUser, error: emailCheckError } = await supabase
        .from("users")
        .select("*")
        .eq("email", email)
        .neq("id", userId)
        .single();

      if (emailCheckError && emailCheckError.code !== "PGRST116") {
        throw emailCheckError;
      }

      if (existingUser) {
        return NextResponse.json(
          { error: "Cet email est déjà utilisé" },
          { status: 400 }
        );
      }
    }

    // Mettre à jour l'utilisateur
    const updateData: any = {};
    if (name) updateData.name = name;
    if (email) updateData.email = email;

    const { data: updatedUser, error: updateError } = await supabase
      .from("users")
      .update(updateData)
      .eq("id", userId)
      .select()
      .single();

    if (updateError) {
      throw updateError;
    }

    if (!updatedUser) {
      return NextResponse.json(
        { error: "Échec de la mise à jour de l'utilisateur" },
        { status: 500 }
      );
    }

    return NextResponse.json({
      user: {
        id: updatedUser.id,
        pubkey: updatedUser.pubkey,
        name: updatedUser.name,
        email: updatedUser.email,
      },
    });
  } catch (error) {
    console.error("Erreur lors de la mise à jour du profil:", error);
    return NextResponse.json(
      { error: "Erreur interne du serveur" },
      { status: 500 }
    );
  }
}
