import { NextResponse } from "next/server";
import { headers } from "next/headers";
import { authOptions } from "../../lib/auth";
import { getToken } from "next-auth/jwt";
import { supabase } from "../../lib/supabase";
import type { NextRequest } from "next/server";

// Marquer cette route comme dynamique
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const { amount, description } = await request.json();

    const { data, error } = await supabase
      .from("checkout_sessions")
      .insert({
        amount,
        description,
        status: "pending",
      })
      .select()
      .single();

    if (error) throw error;

    return NextResponse.json(data);
  } catch (error) {
    console.error("Erreur lors de la création de la session:", error);
    return NextResponse.json(
      { error: "Erreur lors de la création de la session" },
      { status: 500 }
    );
  }
}

export async function GET(req: NextRequest) {
  try {
    const token = await getToken({ req });
    if (!token) {
      return NextResponse.json(
        { error: "Vous devez être connecté" },
        { status: 401 }
      );
    }

    // Récupérer l'email de l'utilisateur depuis le token
    const userEmail = token.email;

    // Vérifier si l'utilisateur existe dans la base de données
    const { data: user, error: userError } = await supabase
      .from("users")
      .select("*")
      .eq("email", userEmail)
      .single();

    if (userError || !user) {
      return NextResponse.json(
        { error: "Utilisateur non trouvé" },
        { status: 404 }
      );
    }

    // Créer une session de paiement
    const { data: session, error: sessionError } = await supabase
      .from("payment_sessions")
      .insert([
        {
          user_id: user.id,
          amount: 400000, // 400,000 sats
          status: "pending",
        },
      ])
      .select()
      .single();

    if (sessionError || !session) {
      return NextResponse.json(
        { error: "Erreur lors de la création de la session" },
        { status: 500 }
      );
    }

    return NextResponse.json({
      sessionId: session.id,
      amount: session.amount,
      status: session.status,
    });
  } catch (error) {
    console.error("Error in checkout route:", error);
    return NextResponse.json(
      { error: "Une erreur est survenue" },
      { status: 500 }
    );
  }
}

export async function PATCH(req: NextRequest) {
  try {
    const token = await getToken({ req });
    if (!token) {
      return NextResponse.json(
        { error: "Vous devez être connecté" },
        { status: 401 }
      );
    }

    const body = await req.json();
    const { sessionId } = body;

    if (!sessionId) {
      return NextResponse.json(
        { error: "ID de session manquant" },
        { status: 400 }
      );
    }

    // Mettre à jour le statut de la session
    const { data: session, error: sessionError } = await supabase
      .from("payment_sessions")
      .update({ status: "completed" })
      .eq("id", sessionId)
      .select()
      .single();

    if (sessionError || !session) {
      return NextResponse.json(
        { error: "Session non trouvée" },
        { status: 404 }
      );
    }

    return NextResponse.json({
      sessionId: session.id,
      status: session.status,
    });
  } catch (error) {
    console.error("Error updating payment session:", error);
    return NextResponse.json(
      { error: "Une erreur est survenue" },
      { status: 500 }
    );
  }
}
