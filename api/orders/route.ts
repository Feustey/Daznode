import { NextRequest, NextResponse } from "next/server";
import { supabase } from "../../lib/supabase";
import { generateId } from "@/utils/id";

// Marquer cette route comme dynamique
export const dynamic = "force-dynamic";

// GET /api/orders - Récupérer toutes les commandes d'un utilisateur
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get("userId");

    if (!userId) {
      return NextResponse.json(
        { error: "userId is required" },
        { status: 400 }
      );
    }

    const { data: orders, error } = await supabase
      .from("orders")
      .select("*")
      .eq("user_id", userId)
      .order("created_at", { ascending: false });

    if (error) {
      throw error;
    }

    return NextResponse.json(orders);
  } catch (error) {
    console.error("Error fetching orders:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

// POST /api/orders - Créer une nouvelle commande
export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { userId, items, totalAmount } = body;

    if (!userId || !items || !totalAmount) {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      );
    }

    const { data: order, error } = await supabase
      .from("orders")
      .insert({
        user_id: userId,
        items,
        total_amount: totalAmount,
        status: "pending",
      })
      .select()
      .single();

    if (error) {
      throw error;
    }

    return NextResponse.json(order, { status: 201 });
  } catch (error) {
    console.error("Error creating order:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
