import { NextRequest, NextResponse } from "next/server";
import { supabase } from "../../../lib/supabase";

export async function PUT(req: NextRequest) {
  try {
    const { orderId, status } = await req.json();

    if (!orderId || !status) {
      return NextResponse.json(
        { error: "ID de commande et statut requis" },
        { status: 400 }
      );
    }

    const { data: order, error: getError } = await supabase
      .from("orders")
      .select("*")
      .eq("id", orderId)
      .single();

    if (getError || !order) {
      return NextResponse.json(
        { error: "Commande non trouvée" },
        { status: 404 }
      );
    }

    const { data: updatedOrder, error: updateError } = await supabase
      .from("orders")
      .update({ status })
      .eq("id", orderId)
      .select()
      .single();

    if (updateError) {
      throw updateError;
    }

    return NextResponse.json({
      message: "Statut de la commande mis à jour avec succès",
      order: updatedOrder,
    });
  } catch (error) {
    console.error("Erreur lors de la mise à jour du statut:", error);
    return NextResponse.json(
      { error: "Erreur interne du serveur" },
      { status: 500 }
    );
  }
}
