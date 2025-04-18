import { supabase } from "../lib/supabase";
import { getAlbyService } from "./albyService";

const ALBY_API_URL = "https://api.getalby.com";

interface CreateWebhookParams {
  userId: string;
  url: string;
  description: string;
  filterTypes: string[];
}

interface WebhookResponse {
  url: string;
  description: string;
  filter_types: string[];
  created_at: string;
  id: string;
  endpoint_secret: string;
}

export class AlbyWebhookService {
  private static async makeRequest(
    endpoint: string,
    options: RequestInit = {}
  ) {
    const response = await fetch(`${ALBY_API_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`Alby API error: ${response.statusText}`);
    }

    return response.json();
  }

  static async createWebhook({
    userId,
    url,
    description,
    filterTypes,
  }: CreateWebhookParams): Promise<any> {
    try {
      const albyService = await getAlbyService();
      const response = await albyService.createWebhook({
        url,
        description,
        filterTypes,
      });

      const { data: webhook, error } = await supabase
        .from("alby_webhooks")
        .insert({
          user_id: userId,
          endpoint_id: response.id,
          endpoint_secret: response.endpoint_secret,
          url: response.url,
          description: response.description,
          filter_types: response.filter_types,
        })
        .select()
        .single();

      if (error) throw error;
      return webhook;
    } catch (error) {
      throw error;
    }
  }

  static async getWebhook(endpointId: string): Promise<any | null> {
    try {
      const { data: webhook, error } = await supabase
        .from("alby_webhooks")
        .select("*")
        .eq("endpoint_id", endpointId)
        .single();

      if (error) throw error;
      return webhook;
    } catch (error) {
      console.error("Erreur lors de la récupération du webhook Alby:", error);
      throw error;
    }
  }

  static async deleteWebhook(endpointId: string): Promise<void> {
    try {
      const albyService = await getAlbyService();
      await albyService.deleteWebhook(endpointId);

      const { error } = await supabase
        .from("alby_webhooks")
        .delete()
        .eq("endpoint_id", endpointId);

      if (error) throw error;
    } catch (error) {
      throw error;
    }
  }

  static async getUserWebhooks(userId: string): Promise<any[]> {
    try {
      const { data: webhooks, error } = await supabase
        .from("alby_webhooks")
        .select("*")
        .eq("user_id", userId);

      if (error) throw error;
      return webhooks || [];
    } catch (error) {
      console.error("Erreur lors de la récupération des webhooks Alby:", error);
      throw error;
    }
  }

  static async verifyWebhookSignature(
    payload: string,
    signature: string,
    secret: string
  ): Promise<boolean> {
    try {
      const albyService = await getAlbyService();
      return albyService.verifyWebhookSignature(payload, signature, secret);
    } catch (error) {
      return false;
    }
  }

  static async handleWebhook(payload: any, signature: string) {
    const albyService = await getAlbyService();
    // ... existing code ...
  }
}
