import { Client, auth } from "@getalby/sdk";
import { envVars } from "@/app/lib/env";
import { supabase } from "../lib/supabase";
import { User, CheckoutSession } from "@/app/lib/models";
import crypto from "crypto";

export interface AlbyInvoice {
  payment_request: string;
  payment_hash: string;
  amount: number;
  description?: string;
}

export class AlbyService {
  private client: Client;
  private static instance: AlbyService;
  private apiKey: string;

  private constructor() {
    const authClient = new auth.OAuth2User({
      client_id: process.env.NEXT_PUBLIC_ALBY_PUBLIC_KEY || "",
      client_secret: process.env.ALBY_SECRET || "",
      callback: `${process.env.NEXT_PUBLIC_APP_URL}/api/auth/callback/alby`,
      scopes: ["invoices:read", "invoices:create"],
      user_agent: "DazLng/1.0.0",
    });
    this.client = new Client(authClient);
    this.apiKey = process.env.ALBY_API_KEY || "";
    if (!this.apiKey) {
      throw new Error("ALBY_API_KEY is not set");
    }
  }

  public static async getInstance(): Promise<AlbyService> {
    if (!AlbyService.instance) {
      AlbyService.instance = new AlbyService();
    }
    return AlbyService.instance;
  }

  /**
   * Crée une nouvelle facture Lightning
   */
  async createInvoice(
    amount: number,
    description?: string
  ): Promise<AlbyInvoice> {
    const invoice = await this.client.createInvoice({
      amount,
      description,
    });

    return {
      payment_request: invoice.payment_request,
      payment_hash: invoice.payment_hash,
      amount,
      description,
    };
  }

  /**
   * Crée un webhook pour recevoir les notifications de paiement
   */
  async createWebhook(params: {
    url: string;
    description: string;
    filterTypes: string[];
  }) {
    return this.client.createWebhookEndpoint({
      url: params.url,
      description: params.description,
      filter_types: params.filterTypes,
    });
  }

  /**
   * Récupère les clés Nostr associées au compte
   */
  async getNostrKeys() {
    const accountInfo = await this.client.accountInformation({});
    return {
      pubkey: accountInfo.nostr_pubkey,
    };
  }

  /**
   * Vérifie la signature d'un webhook
   */
  verifyWebhookSignature(
    payload: string,
    signature: string,
    secret: string
  ): boolean {
    const hmac = crypto.createHmac("sha256", secret);
    hmac.update(payload);
    const expectedSignature = hmac.digest("hex");
    return crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(expectedSignature)
    );
  }

  /**
   * Envoie un paiement
   */
  async sendPayment(params: { invoice: string }) {
    return this.client.sendPayment(params);
  }

  /**
   * Gère une notification de paiement
   */
  async handlePaymentWebhook(payload: any) {
    const { payment_hash, status } = payload;

    if (status === "paid") {
      const { data: session } = await supabase
        .from("checkout_sessions")
        .select("*")
        .eq("payment_hash", payment_hash)
        .single();

      if (session) {
        await this.sendPaymentNotification(session);
        await supabase
          .from("checkout_sessions")
          .update({ status: "completed" })
          .eq("id", session.id);
      }
    }
  }

  /**
   * Envoie une notification de paiement
   */
  private async sendPaymentNotification(session: CheckoutSession) {
    const { data: user } = await supabase
      .from("users")
      .select("*")
      .eq("id", session.user_id)
      .single();

    if (user) {
      // Envoyer une notification à l'utilisateur
      // TODO: Implémenter la notification
    }
  }

  /**
   * Supprime un webhook
   */
  async deleteWebhook(endpointId: string) {
    return this.client.deleteWebhookEndpoint(endpointId);
  }

  /**
   * Vérifie le statut d'une facture
   */
  async checkInvoiceStatus(invoice: string) {
    const invoiceData = await this.client.getInvoice(invoice);
    return invoiceData.settled;
  }

  /**
   * Récupère une facture
   */
  async getInvoice(invoiceId: string) {
    return this.client.getInvoice(invoiceId);
  }
}

export const getAlbyService = async () => {
  return AlbyService.getInstance();
};

export const createInvoice = async (
  amount: number,
  description?: string
): Promise<AlbyInvoice> => {
  const service = await getAlbyService();
  return service.createInvoice(amount, description);
};

export const checkInvoiceStatus = async (
  paymentHash: string
): Promise<boolean> => {
  const service = await getAlbyService();
  return service.checkInvoiceStatus(paymentHash);
};
