import { supabase } from "../../../lib/supabase";
import {
  createInvoice,
  checkInvoiceStatus,
} from "../../../services/albyService";
import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const { amount, description } = await request.json();

    // Créer une facture Alby
    const invoice = await createInvoice(amount, description);

    // Enregistrer la session de paiement dans Supabase
    const { data, error } = await supabase
      .from("checkout_sessions")
      .insert({
        amount,
        description,
        payment_hash: invoice.payment_hash,
        payment_request: invoice.payment_request,
        status: "pending",
      })
      .select()
      .single();

    if (error) throw error;

    return NextResponse.json({
      ...invoice,
      session_id: data.id,
    });
  } catch (error) {
    console.error("Erreur lors du traitement du paiement:", error);
    return NextResponse.json(
      { error: "Erreur lors du traitement du paiement" },
      { status: 500 }
    );
  }
}
