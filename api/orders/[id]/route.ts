import { NextRequest, NextResponse } from "next/server";
import { supabase } from "../../../lib/supabase";

// GET /api/orders/[id] - Récupérer une commande spécifique
export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const orderId = params.id;

    const { data: order, error } = await supabase
      .from("orders")
      .select("*")
      .eq("id", orderId)
      .single();

    if (error) {
      throw error;
    }

    if (!order) {
      return NextResponse.json(
        { error: "Commande non trouvée" },
        { status: 404 }
      );
    }

    return NextResponse.json(order);
  } catch (error) {
    console.error("Erreur lors de la récupération de la commande:", error);
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}

// PUT /api/orders/[id] - Mettre à jour une commande
export async function PUT(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const orderId = params.id;
    const body = await req.json();
    const { status, paymentStatus, trackingNumber, notes } = body;

    // Vérifier si la commande existe
    const { data: order, error: getError } = await supabase
      .from("orders")
      .select("*")
      .eq("id", orderId)
      .single();

    if (getError) {
      throw getError;
    }

    if (!order) {
      return NextResponse.json(
        { error: "Commande non trouvée" },
        { status: 404 }
      );
    }

    // Préparer les données de mise à jour
    const updateData: any = {};
    if (status) updateData.status = status;
    if (paymentStatus) updateData.payment_status = paymentStatus;
    if (trackingNumber !== undefined)
      updateData.tracking_number = trackingNumber;
    if (notes !== undefined) updateData.notes = notes;

    // Mettre à jour la commande
    const { data: updatedOrder, error: updateError } = await supabase
      .from("orders")
      .update(updateData)
      .eq("id", orderId)
      .select()
      .single();

    if (updateError) {
      throw updateError;
    }

    return NextResponse.json(updatedOrder);
  } catch (error) {
    console.error("Erreur lors de la mise à jour de la commande:", error);
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}

// DELETE /api/orders/[id] - Supprimer une commande
export async function DELETE(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const orderId = params.id;

    // Vérifier si la commande existe
    const { data: order, error: getError } = await supabase
      .from("orders")
      .select("*")
      .eq("id", orderId)
      .single();

    if (getError) {
      throw getError;
    }

    if (!order) {
      return NextResponse.json(
        { error: "Commande non trouvée" },
        { status: 404 }
      );
    }

    // Vérifier si la commande peut être supprimée (pas de commandes en cours)
    if (order.status !== "cancelled" && order.status !== "delivered") {
      return NextResponse.json(
        {
          error:
            "Seules les commandes annulées ou livrées peuvent être supprimées",
        },
        { status: 400 }
      );
    }

    // Supprimer la commande
    const { error: deleteError } = await supabase
      .from("orders")
      .delete()
      .eq("id", orderId);

    if (deleteError) {
      throw deleteError;
    }

    return NextResponse.json(
      { message: "Commande supprimée avec succès" },
      { status: 200 }
    );
  } catch (error) {
    console.error("Erreur lors de la suppression de la commande:", error);
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}
