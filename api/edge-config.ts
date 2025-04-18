import { NextResponse } from "next/server";

// Configuration pour forcer le rendu dynamique
export const dynamic = "force-dynamic";

// Headers CORS
export function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
  };
}

// Réponses d'erreur standardisées
export const errorResponse = (message: string, status = 500) => {
  return new Response(JSON.stringify({ error: message }), {
    status,
    headers: { "Content-Type": "application/json" },
  });
};

// Réponses de succès standardisées
export const successResponse = (data: any) => {
  return new Response(JSON.stringify(data), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
};
