import { NextResponse } from "next/server";
import { sendVerificationEmail } from "../../../lib/email";

export async function POST(request: Request) {
  try {
    const { email } = await request.json();

    if (!email) {
      return NextResponse.json(
        { error: "L'email est requis" },
        { status: 400 }
      );
    }

    const code = Math.floor(100000 + Math.random() * 900000).toString();
    const result = await sendVerificationEmail(email, code);

    if (result) {
      return NextResponse.json(
        { message: "Email envoyé avec succès", code },
        { status: 200 }
      );
    } else {
      return NextResponse.json(
        { error: "Erreur lors de l'envoi de l'email" },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error("Erreur lors du test d'envoi d'email:", error);
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}
