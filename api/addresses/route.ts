import { NextRequest, NextResponse } from "next/server";
import { supabase } from "../../lib/supabase";
import { getToken } from "next-auth/jwt";

// GET /api/addresses - Récupérer toutes les adresses d'un utilisateur
export async function GET(req: NextRequest) {
  try {
    const token = await getToken({ req });
    if (!token) {
      return NextResponse.json(
        { error: "Vous devez être connecté" },
        { status: 401 }
      );
    }

    const userId = token.sub;
    const { data: addresses, error } = await supabase
      .from("addresses")
      .select("*")
      .eq("user_id", userId);

    if (error) {
      throw error;
    }

    return NextResponse.json(addresses);
  } catch (error) {
    console.error("Erreur lors de la récupération des adresses:", error);
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}

// POST /api/addresses - Créer une nouvelle adresse
export async function POST(req: NextRequest) {
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

    // Si c'est l'adresse par défaut, mettre à jour les autres adresses
    if (is_default) {
      const { error: updateError } = await supabase
        .from("addresses")
        .update({ is_default: false })
        .eq("user_id", token.sub)
        .eq("type", type)
        .eq("is_default", true);

      if (updateError) {
        throw updateError;
      }
    }

    // Créer la nouvelle adresse
    const { data: newAddress, error: insertError } = await supabase
      .from("addresses")
      .insert({
        user_id: token.sub,
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
      .select()
      .single();

    if (insertError) {
      throw insertError;
    }

    return NextResponse.json(newAddress, { status: 201 });
  } catch (error) {
    console.error("Erreur lors de la création de l'adresse:", error);
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}
