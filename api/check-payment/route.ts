import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const payment_hash = req.nextUrl.searchParams.get("payment_hash");

  try {
    const res = await fetch(
      `https://api.getalby.com/payments/${payment_hash}`,
      {
        headers: {
          Authorization: `Bearer ${process.env.ALBY_API_KEY}`,
        },
      }
    );

    if (!res.ok) {
      throw new Error("Erreur lors de la vérification du paiement");
    }

    const payment = await res.json();
    return NextResponse.json({ paid: payment?.paid || false });
  } catch (error) {
    console.error("Erreur lors de la vérification du paiement:", error);
    return NextResponse.json(
      { error: "Erreur lors de la vérification du paiement" },
      { status: 500 }
    );
  }
}
