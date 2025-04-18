"use client";

import { getAlbyService } from "./albyService";
import { supabase } from "@/app/lib/supabase";
import { CheckoutSession } from "@/app/lib/models";
import { productService } from "./productService";

export interface CheckoutSessionData {
  id: string;
  amount: number;
  currency: string;
  status: string;
  plan?: string;
  billingCycle?: string;
  metadata?: {
    nodeType?: string;
    subscriptionId?: string;
    features?: string[];
  };
  deliveryInfo?: {
    name: string;
    email: string;
    phone?: string;
    company?: string;
    address?: string;
    city?: string;
    zipCode?: string;
    country?: string;
  };
  paymentInfo?: {
    method: string;
    status: string;
    hash?: string;
  };
}

class CheckoutService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || "";
  }

  async createCheckoutSession(amount: number): Promise<CheckoutSessionData> {
    try {
      const response = await fetch(`${this.baseUrl}/checkout/create`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ amount }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Error creating checkout session:", error);
      throw error;
    }
  }

  async getSessionStatus(sessionId: string): Promise<CheckoutSessionData> {
    try {
      const response = await fetch(
        `${this.baseUrl}/checkout/status/${sessionId}`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Error getting session status:", error);
      throw error;
    }
  }

  async createSession(data: Partial<CheckoutSessionData>) {
    try {
      const { data: session, error } = await supabase
        .from("checkout_sessions")
        .insert({
          plan: data.plan,
          amount: data.amount,
          currency: data.currency,
          status: data.status,
          metadata: data.metadata,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        })
        .select()
        .single();

      if (error) throw error;
      return session;
    } catch (error) {
      console.error("Error creating checkout session:", error);
      throw error;
    }
  }

  async getSession(sessionId: string) {
    try {
      const { data: session, error } = await supabase
        .from("checkout_sessions")
        .select("*")
        .eq("id", sessionId)
        .single();

      if (error) throw error;
      return session;
    } catch (error) {
      console.error("Error getting checkout session:", error);
      throw error;
    }
  }

  async updateSession(sessionId: string, data: Partial<CheckoutSessionData>) {
    try {
      const { data: session, error } = await supabase
        .from("checkout_sessions")
        .update({
          plan: data.plan,
          amount: data.amount,
          currency: data.currency,
          status: data.status,
          metadata: data.metadata,
          updated_at: new Date().toISOString(),
        })
        .eq("id", sessionId)
        .select()
        .single();

      if (error) throw error;
      return session;
    } catch (error) {
      console.error("Error updating checkout session:", error);
      throw error;
    }
  }

  async processPayment(sessionId: string) {
    try {
      const session = await this.getSession(sessionId);
      const albyService = await getAlbyService();
      const invoice = await albyService.createInvoice(
        session.amount,
        `Payment for session ${sessionId}`
      );

      // Confirmer le stock une fois le paiement initié
      if (session.products) {
        const stockConfirmed = await productService.confirmStock(
          session.user_id
        );
        if (!stockConfirmed) {
          throw new Error("Failed to confirm stock");
        }
      }

      await this.updateSession(sessionId, {
        paymentInfo: {
          paymentUrl: invoice.payment_request,
        },
      });

      return invoice;
    } catch (error) {
      // En cas d'erreur, libérer les stocks réservés
      const session = await this.getSession(sessionId);
      if (session.products) {
        await productService.releaseStock(session.user_id);
      }
      console.error("Error processing payment:", error);
      throw error;
    }
  }
}

export const checkoutService = new CheckoutService();
