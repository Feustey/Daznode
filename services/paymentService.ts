import { supabase } from "@/app/lib/supabase";
import { mcpService } from "./mcpService";

export interface Payment {
  id: string;
  sourceNodeId: string;
  targetNodeId: string;
  amount: number;
  status: "pending" | "completed" | "failed";
  timestamp: Date;
  fee?: number;
  route?: string[];
}

export class PaymentService {
  // Envoyer un paiement
  async sendPayment(
    sourceNodeId: string,
    targetNodeId: string,
    amount: number
  ): Promise<Payment> {
    try {
      // Créer un enregistrement de paiement dans Supabase
      const { data: payment, error } = await supabase
        .from("payments")
        .insert({
          source_node_id: sourceNodeId,
          target_node_id: targetNodeId,
          amount,
          status: "pending",
          timestamp: new Date().toISOString(),
        })
        .select()
        .single();

      if (error) throw error;

      // Utiliser MCP pour envoyer le paiement
      const mcpPayment = await mcpService.sendPayment(
        sourceNodeId,
        amount,
        targetNodeId
      );

      // Mettre à jour le paiement dans Supabase
      await supabase
        .from("payments")
        .update({
          status: mcpPayment.status,
          fee: mcpPayment.fee,
          route: mcpPayment.route,
        })
        .eq("id", payment.id);

      return {
        id: payment.id,
        sourceNodeId,
        targetNodeId,
        amount,
        status: mcpPayment.status || "pending",
        timestamp: new Date(payment.timestamp),
        fee: mcpPayment.fee,
        route: mcpPayment.route,
      };
    } catch (error) {
      console.error("Error sending payment:", error);
      throw error;
    }
  }

  // Obtenir le statut d'un paiement
  async getPaymentStatus(paymentId: string): Promise<Payment> {
    try {
      const { data: payment, error } = await supabase
        .from("payments")
        .select("*")
        .eq("id", paymentId)
        .single();

      if (error) throw error;

      return {
        id: payment.id,
        sourceNodeId: payment.source_node_id,
        targetNodeId: payment.target_node_id,
        amount: payment.amount,
        status: payment.status || "pending",
        timestamp: new Date(payment.timestamp),
        fee: payment.fee,
        route: payment.route,
      };
    } catch (error) {
      console.error("Error getting payment status:", error);
      throw error;
    }
  }

  // Trouver une route pour un paiement
  async findRoute(
    sourceNodeId: string,
    targetNodeId: string,
    amount: number
  ): Promise<{ path: string[]; fee: number }> {
    try {
      // Utiliser MCP pour trouver une route
      const route = await mcpService.findRoute(
        sourceNodeId,
        targetNodeId,
        amount
      );

      return {
        path: route.path,
        fee: route.fee,
      };
    } catch (error) {
      console.error("Error finding route with MCP:", error);
      throw error;
    }
  }

  // Récupérer l'historique des transactions
  async getTransactions(): Promise<Payment[]> {
    try {
      const { data: payments, error } = await supabase
        .from("payments")
        .select("*")
        .order("timestamp", { ascending: false });

      if (error) throw error;

      return payments.map((payment) => ({
        id: payment.id,
        sourceNodeId: payment.source_node_id,
        targetNodeId: payment.target_node_id,
        amount: payment.amount,
        status: payment.status || "pending",
        timestamp: new Date(payment.timestamp),
        fee: payment.fee,
        route: payment.route,
      }));
    } catch (error) {
      console.error("Error getting transactions:", error);
      throw error;
    }
  }
}

export const paymentService = new PaymentService();
