import { NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";

export async function GET() {
  const session = await getServerSession(authOptions);

  if (!session) {
    return NextResponse.json({ error: "Non autorisé" }, { status: 401 });
  }

  try {
    // TODO: Récupérer les données utilisateur depuis la base de données
    const userData = {
      name: session.user?.name,
      email: session.user?.email,
      phone: "",
      address: "",
      settings: {
        emailNotifications: true,
        smsNotifications: false,
        darkMode: false,
        language: "fr",
      },
    };

    return NextResponse.json(userData);
  } catch (error) {
    return NextResponse.json(
      { error: "Erreur lors de la récupération des données" },
      { status: 500 }
    );
  }
}

export async function PUT(request: Request) {
  const session = await getServerSession(authOptions);

  if (!session) {
    return NextResponse.json({ error: "Non autorisé" }, { status: 401 });
  }

  try {
    const data = await request.json();

    // TODO: Mettre à jour les données utilisateur dans la base de données

    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json(
      { error: "Erreur lors de la mise à jour des données" },
      { status: 500 }
    );
  }
}
