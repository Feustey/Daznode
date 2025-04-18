import { NextResponse } from "next/server";
import { supabase } from "../../../../lib/supabase";

export const dynamic = "force-dynamic";

export async function GET(
  request: Request,
  { params }: { params: { sessionId: string } }
) {
  try {
    const { data: session, error } = await supabase
      .from("checkout_sessions")
      .select("*")
      .eq("id", params.sessionId)
      .single();

    if (error) {
      throw error;
    }

    if (!session) {
      return NextResponse.json({ error: "Session not found" }, { status: 404 });
    }

    return NextResponse.json({
      id: session.id,
      amount: session.amount,
      paymentUrl: session.payment_url,
      status: session.status,
    });
  } catch (error) {
    console.error("Error fetching session:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
