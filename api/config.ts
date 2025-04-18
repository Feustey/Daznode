import { NextResponse } from "next/server";
import { supabase } from "../lib/supabase";

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

export async function withDb(handler: Function) {
  return async (...args: any[]) => {
    try {
      // Vérifier la connexion à Supabase
      const { data, error } = await supabase
        .from("config")
        .select("*")
        .limit(1);

      if (error) {
        throw error;
      }

      return handler(...args);
    } catch (error) {
      console.error("Database error:", error);
      return new Response(JSON.stringify({ error: "Database error" }), {
        status: 500,
        headers: { "Content-Type": "application/json" },
      });
    }
  };
}
