import { NextRequest, NextResponse } from "next/server";
import { supabase } from "../../../lib/supabase";
import { auth } from "../../../lib/auth";
import { AlbyWebhookService } from "../../../services/albyWebhook";

export async function POST(req: NextRequest) {
  try {
    const session = await auth();
    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { url, description, filterTypes } = await req.json();

    if (!url || !description || !filterTypes) {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      );
    }

    const webhook = await AlbyWebhookService.createWebhook({
      userId: session.user.id,
      url,
      description,
      filterTypes,
    });

    return NextResponse.json(webhook);
  } catch (error) {
    console.error("Error creating webhook:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

export async function GET(req: NextRequest) {
  try {
    const session = await auth();
    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const webhooks = await AlbyWebhookService.getUserWebhooks(session.user.id);
    return NextResponse.json(webhooks);
  } catch (error) {
    console.error("Error getting webhooks:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
