import { NextResponse } from "next/server";
import { auth } from "../../lib/auth";
import { chatRouter } from "../../services/chatService";
import { getCurrentUser } from "../../lib/auth";
import { Headers } from "next/dist/compiled/@edge-runtime/primitives";

export async function POST(req: Request) {
  try {
    const session = await auth();
    if (!session) {
      return NextResponse.json({ error: "Non autorisé" }, { status: 401 });
    }

    const headers = req.headers;
    const user = await getCurrentUser();
    const body = await req.json();

    const result = await chatRouter
      .createCaller({ session, headers })
      .sendMessage(body);

    return NextResponse.json(result);
  } catch (error) {
    console.error("Erreur lors du traitement de la requête:", error);
    return NextResponse.json(
      { error: "Erreur interne du serveur" },
      { status: 500 }
    );
  }
}
