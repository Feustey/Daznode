import { NextRequest, NextResponse } from "next/server";
import { supabase } from "../../../lib/supabase";
import { getToken } from "next-auth/jwt";

// GET /api/addresses/[id] - Récupérer une adresse spécifique
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

    const { data: address, error } = await supabase
      .from("addresses")
      .select("*")
      .eq("id", params.id)
      .eq("user_id", token.sub)
      .single();

    if (error) {
      throw error;
    }

    if (!address) {
      return NextResponse.json(
        { error: "Adresse non trouvée" },
        { status: 404 }
      );
    }

    return NextResponse.json(address);
  } catch (error) {
    console.error("Erreur lors de la récupération de l'adresse:", error);
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}

// PUT /api/addresses/[id] - Mettre à jour une adresse
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

    const body = await req.json();
    const {
      type,
      first_name,
      last_name,
      street,
      street2,
      city,
      state,
      postal_code,
      country,
      is_default,
      phone_number,
    } = body;

    // Vérifier si l'adresse existe et appartient à l'utilisateur
    const { data: existingAddress, error: checkError } = await supabase
      .from("addresses")
      .select("*")
      .eq("id", params.id)
      .eq("user_id", token.sub)
      .single();

    if (checkError) {
      throw checkError;
    }

    if (!existingAddress) {
      return NextResponse.json(
        { error: "Adresse non trouvée" },
        { status: 404 }
      );
    }

    // Si c'est l'adresse par défaut, mettre à jour les autres adresses
    if (is_default) {
      const { error: updateError } = await supabase
        .from("addresses")
        .update({ is_default: false })
        .eq("user_id", token.sub)
        .eq("type", type)
        .eq("is_default", true)
        .neq("id", params.id);

      if (updateError) {
        throw updateError;
      }
    }

    // Mettre à jour l'adresse
    const { data: updatedAddress, error: updateError } = await supabase
      .from("addresses")
      .update({
        type,
        first_name,
        last_name,
        street,
        street2,
        city,
        state,
        postal_code,
        country,
        is_default,
        phone_number,
      })
      .eq("id", params.id)
      .eq("user_id", token.sub)
      .select()
      .single();

    if (updateError) {
      throw updateError;
    }

    return NextResponse.json(updatedAddress);
  } catch (error) {
    console.error("Erreur lors de la mise à jour de l'adresse:", error);
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}

// DELETE /api/addresses/[id] - Supprimer une adresse
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

    // Vérifier si l'adresse existe et appartient à l'utilisateur
    const { data: address, error: checkError } = await supabase
      .from("addresses")
      .select("*")
      .eq("id", params.id)
      .eq("user_id", token.sub)
      .single();

    if (checkError) {
      throw checkError;
    }

    if (!address) {
      return NextResponse.json(
        { error: "Adresse non trouvée" },
        { status: 404 }
      );
    }

    // Supprimer l'adresse
    const { error: deleteError } = await supabase
      .from("addresses")
      .delete()
      .eq("id", params.id)
      .eq("user_id", token.sub);

    if (deleteError) {
      throw deleteError;
    }

    return NextResponse.json(
      { message: "Adresse supprimée avec succès" },
      { status: 200 }
    );
  } catch (error) {
    console.error("Erreur lors de la suppression de l'adresse:", error);
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}
