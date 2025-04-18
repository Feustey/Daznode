import { NextRequest, NextResponse } from "next/server";
import { supabase } from "../../../lib/supabase";

export async function DELETE(req: NextRequest) {
  try {
    const { userId } = await req.json();

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

    // Supprimer toutes les sessions de l'utilisateur
    const { error: deleteSessionsError } = await supabase
      .from("sessions")
      .delete()
      .eq("user_id", userId);

    if (deleteSessionsError) {
      throw deleteSessionsError;
    }

    // Supprimer l'utilisateur
    const { error: deleteUserError } = await supabase
      .from("users")
      .delete()
      .eq("id", userId);

    if (deleteUserError) {
      throw deleteUserError;
    }

    return NextResponse.json({
      message: "Compte supprimé avec succès",
    });
  } catch (error) {
    console.error("Erreur lors de la suppression du compte:", error);
    return NextResponse.json(
      { error: "Erreur interne du serveur" },
      { status: 500 }
    );
  }
}
