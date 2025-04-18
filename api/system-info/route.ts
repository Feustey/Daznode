import { NextResponse } from "next/server";

export async function GET() {
  try {
    const systemInfo = {
      version: process.env.npm_package_version || "0.1.0",
      nodeVersion: process.version,
      platform: process.platform,
      arch: process.arch,
      env: process.env.NODE_ENV,
      variables: {
        NEXTAUTH_URL: process.env.NEXTAUTH_URL ? "Définie" : "Non définie",
        NEXTAUTH_SECRET: process.env.NEXTAUTH_SECRET
          ? "Définie"
          : "Non définie",
        SUPABASE_URL: process.env.SUPABASE_URL ? "Définie" : "Non définie",
        SUPABASE_ANON_KEY: process.env.SUPABASE_ANON_KEY
          ? "Définie"
          : "Non définie",
        SUPABASE_SERVICE_ROLE_KEY: process.env.SUPABASE_SERVICE_ROLE_KEY
          ? "Définie"
          : "Non définie",
      },
    };

    return NextResponse.json(systemInfo);
  } catch (error) {
    console.error(
      "Erreur lors de la récupération des informations système:",
      error
    );
    return NextResponse.json(
      { error: "Erreur lors de la récupération des informations système" },
      { status: 500 }
    );
  }
}
