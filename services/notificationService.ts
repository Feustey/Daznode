import { supabase } from "@/app/lib/supabase";
import { mcpService } from "./mcpService";

export interface Notification {
  id: string;
  user_id: string;
  type: "info" | "success" | "warning" | "error";
  title: string;
  message: string;
  read: boolean;
  created_at: Date;
}

export class NotificationService {
  // Créer une nouvelle notification
  async createNotification(
    userId: string,
    type: Notification["type"],
    title: string,
    message: string
  ): Promise<Notification> {
    try {
      const { data: notification, error } = await supabase
        .from("notifications")
        .insert({
          user_id: userId,
          type,
          title,
          message,
          read: false,
        })
        .select()
        .single();

      if (error) throw error;

      // Envoyer la notification via MCP
      await mcpService.sendNotification({
        userId,
        type,
        title,
        message,
      });

      return {
        id: notification.id,
        user_id: notification.user_id,
        type: notification.type,
        title: notification.title,
        message: notification.message,
        read: notification.read,
        created_at: new Date(notification.created_at),
      };
    } catch (error) {
      console.error("Error creating notification:", error);
      throw error;
    }
  }

  // Obtenir les notifications d'un utilisateur
  async getUserNotifications(userId: string): Promise<Notification[]> {
    try {
      const { data: notifications, error } = await supabase
        .from("notifications")
        .select("*")
        .eq("user_id", userId)
        .order("created_at", { ascending: false });

      if (error) throw error;

      return notifications.map((notification) => ({
        id: notification.id,
        user_id: notification.user_id,
        type: notification.type,
        title: notification.title,
        message: notification.message,
        read: notification.read,
        created_at: new Date(notification.created_at),
      }));
    } catch (error) {
      console.error("Error getting user notifications:", error);
      throw error;
    }
  }

  // Marquer une notification comme lue
  async markAsRead(notificationId: string): Promise<boolean> {
    try {
      const { error } = await supabase
        .from("notifications")
        .update({ read: true })
        .eq("id", notificationId);

      if (error) throw error;
      return true;
    } catch (error) {
      console.error("Error marking notification as read:", error);
      throw error;
    }
  }

  // Supprimer une notification
  async deleteNotification(notificationId: string): Promise<boolean> {
    try {
      const { error } = await supabase
        .from("notifications")
        .delete()
        .eq("id", notificationId);

      if (error) throw error;
      return true;
    } catch (error) {
      console.error("Error deleting notification:", error);
      throw error;
    }
  }

  // Supprimer toutes les notifications d'un utilisateur
  async deleteUserNotifications(userId: string): Promise<boolean> {
    try {
      const { error } = await supabase
        .from("notifications")
        .delete()
        .eq("user_id", userId);

      if (error) throw error;
      return true;
    } catch (error) {
      console.error("Error deleting user notifications:", error);
      throw error;
    }
  }

  // Obtenir le nombre de notifications non lues
  async getUnreadCount(userId: string): Promise<number> {
    try {
      const { count, error } = await supabase
        .from("notifications")
        .select("*", { count: "exact", head: true })
        .eq("user_id", userId)
        .eq("read", false);

      if (error) throw error;
      return count || 0;
    } catch (error) {
      console.error("Error getting unread count:", error);
      throw error;
    }
  }
}

export const notificationService = new NotificationService();
