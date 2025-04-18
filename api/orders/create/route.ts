import { NextRequest, NextResponse } from "next/server";
import { supabase } from "../../../lib/supabase";

export async function POST(req: NextRequest) {
  try {
    const { userId, items, total } = await req.json();

    if (!userId || !items || !total) {
      return NextResponse.json(
        { error: "Données de commande incomplètes" },
        { status: 400 }
      );
    }

    // Vérifier que tous les produits existent
    for (const item of items) {
      const { data: product, error } = await supabase
        .from("products")
        .select("*")
        .eq("id", item.productId)
        .single();

      if (error || !product) {
        return NextResponse.json(
          { error: `Produit non trouvé: ${item.productId}` },
          { status: 404 }
        );
      }
    }

    // Créer la commande
    const { data: order, error } = await supabase
      .from("orders")
      .insert({
        user_id: userId,
        items: items.map((item: any) => ({
          product_id: item.productId,
          quantity: item.quantity,
          price: item.price,
        })),
        total,
        status: "pending",
      })
      .select()
      .single();

    if (error) {
      throw error;
    }

    return NextResponse.json({
      message: "Commande créée avec succès",
      order,
    });
  } catch (error) {
    console.error("Erreur lors de la création de la commande:", error);
    return NextResponse.json(
      { error: "Erreur interne du serveur" },
      { status: 500 }
    );
  }
}
