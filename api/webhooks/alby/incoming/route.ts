import { NextRequest, NextResponse } from "next/server";
import { AlbyWebhookService } from "@/services/albyWebhook";
import Order from "@/models/Order";
import { supabase } from "@/lib/supabase";

export async function POST(req: NextRequest) {
  try {
    const signature = req.headers.get("x-alby-signature");
    if (!signature) {
      return NextResponse.json({ error: "Missing signature" }, { status: 401 });
    }

    const payload = await req.text();
    const webhook = await AlbyWebhookService.getWebhook(
      req.headers.get("x-alby-endpoint-id") || ""
    );

    if (!webhook) {
      return NextResponse.json(
        { error: "Invalid webhook endpoint" },
        { status: 404 }
      );
    }

    const isValid = AlbyWebhookService.verifyWebhookSignature(
      payload,
      signature,
      webhook.endpointSecret
    );

    if (!isValid) {
      return NextResponse.json({ error: "Invalid signature" }, { status: 401 });
    }

    const data = JSON.parse(payload);

    // Traiter le webhook en fonction du type
    if (data.type === "invoice.incoming.settled") {
      // Mettre à jour le statut de la commande
      await Order.findOneAndUpdate(
        { paymentHash: data.payment_hash },
        {
          $set: {
            status: "paid",
            paidAt: new Date(),
            paymentDetails: {
              amount: data.amount,
              currency: data.currency,
              paymentHash: data.payment_hash,
              settledAt: data.settled_at,
            },
          },
        }
      );
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Error processing webhook:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
