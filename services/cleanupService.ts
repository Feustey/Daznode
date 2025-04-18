import { supabase } from "../lib/supabase";

export async function cleanupExpiredSessions() {
  try {
    const now = new Date().toISOString();
    const { error } = await supabase
      .from("sessions")
      .delete()
      .lt("expires", now);

    if (error) {
      throw error;
    }
  } catch (error) {
    console.error("Erreur lors du nettoyage des sessions expirées:", error);
    throw error;
  }
}
