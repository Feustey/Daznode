import { NextRequest, NextResponse } from "next/server";
import { supabase } from "../../../lib/supabase";

// GET /api/profiles/[id] - Récupérer un profil spécifique
export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const profileId = params.id;

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
      .eq("id", profileId)
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

// PUT /api/profiles/[id] - Mettre à jour un profil
export async function PUT(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const profileId = params.id;
    const body = await req.json();
    const { phoneNumber, avatar, bio, preferences, socialLinks } = body;

    // Vérifier si le profil existe
    const { data: profile, error: getError } = await supabase
      .from("profiles")
      .select("*")
      .eq("id", profileId)
      .single();

    if (getError) {
      throw getError;
    }

    if (!profile) {
      return NextResponse.json({ error: "Profil non trouvé" }, { status: 404 });
    }

    // Préparer les données de mise à jour
    const updateData: any = {};
    if (phoneNumber) updateData.phone_number = phoneNumber;
    if (avatar) updateData.avatar = avatar;
    if (bio) updateData.bio = bio;
    if (preferences) updateData.preferences = preferences;
    if (socialLinks) updateData.social_links = socialLinks;

    // Mettre à jour le profil
    const { data: updatedProfile, error: updateError } = await supabase
      .from("profiles")
      .update(updateData)
      .eq("id", profileId)
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

// DELETE /api/profiles/[id] - Supprimer un profil
export async function DELETE(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const profileId = params.id;

    // Vérifier si le profil existe
    const { data: profile, error: getError } = await supabase
      .from("profiles")
      .select("*")
      .eq("id", profileId)
      .single();

    if (getError) {
      throw getError;
    }

    if (!profile) {
      return NextResponse.json({ error: "Profil non trouvé" }, { status: 404 });
    }

    // Supprimer le profil
    const { error: deleteError } = await supabase
      .from("profiles")
      .delete()
      .eq("id", profileId);

    if (deleteError) {
      throw deleteError;
    }

    return NextResponse.json(
      { message: "Profil supprimé avec succès" },
      { status: 200 }
    );
  } catch (error) {
    console.error("Erreur lors de la suppression du profil:", error);
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}
