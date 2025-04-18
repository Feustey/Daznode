import { NextResponse } from "next/server";
import { supabase } from "../../../lib/supabase";
import { auth } from "../../../lib/auth";

export async function POST(req: Request) {
  try {
    const session = await auth();
    if (!session) {
      return NextResponse.json(
        { error: "Authentication required" },
        { status: 401 }
      );
    }

    const data = await req.json();

    const { data: checkoutSession, error } = await supabase
      .from("checkout_sessions")
      .insert({
        userId: session.user.id,
        ...data,
      })
      .select()
      .single();

    if (error) {
      throw error;
    }

    return NextResponse.json(checkoutSession);
  } catch (error) {
    console.error("Error creating checkout session:", error);
    return NextResponse.json(
      { error: "Failed to create checkout session" },
      { status: 500 }
    );
  }
}

export async function GET(req: Request) {
  try {
    const session = await auth();
    if (!session) {
      return NextResponse.json(
        { error: "Authentication required" },
        { status: 401 }
      );
    }

    const { searchParams } = new URL(req.url);
    const sessionId = searchParams.get("id");

    if (!sessionId) {
      return NextResponse.json(
        { error: "Session ID is required" },
        { status: 400 }
      );
    }

    const { data: checkoutSession, error } = await supabase
      .from("checkout_sessions")
      .select("*")
      .eq("id", sessionId)
      .eq("userId", session.user.id)
      .single();

    if (error) {
      throw error;
    }

    if (!checkoutSession) {
      return NextResponse.json(
        { error: "Checkout session not found" },
        { status: 404 }
      );
    }

    return NextResponse.json(checkoutSession);
  } catch (error) {
    console.error("Error getting checkout session:", error);
    return NextResponse.json(
      { error: "Failed to get checkout session" },
      { status: 500 }
    );
  }
}

export async function PATCH(req: Request) {
  try {
    const session = await auth();
    if (!session) {
      return NextResponse.json(
        { error: "Authentication required" },
        { status: 401 }
      );
    }

    const { searchParams } = new URL(req.url);
    const sessionId = searchParams.get("id");
    const data = await req.json();

    if (!sessionId) {
      return NextResponse.json(
        { error: "Session ID is required" },
        { status: 400 }
      );
    }

    const { data: checkoutSession, error } = await supabase
      .from("checkout_sessions")
      .update(data)
      .eq("id", sessionId)
      .eq("userId", session.user.id)
      .select()
      .single();

    if (error) {
      throw error;
    }

    if (!checkoutSession) {
      return NextResponse.json(
        { error: "Checkout session not found" },
        { status: 404 }
      );
    }

    return NextResponse.json(checkoutSession);
  } catch (error) {
    console.error("Error updating checkout session:", error);
    return NextResponse.json(
      { error: "Failed to update checkout session" },
      { status: 500 }
    );
  }
}
