import NDK from "@nostr-dev-kit/ndk";

interface NWCResponse {
  result: any;
  error?: string;
}

interface NWCRequest {
  method: string;
  params: Record<string, any>;
}

interface Channel {
  id: string;
  state: string;
  capacity: number;
  local_balance: number;
  remote_balance: number;
  remote_pubkey: string;
}

class NWC {
  private ndk: NDK;
  private walletPubkey: string;
  private secret: string;
  private eventHandlers: Map<string, ((data: any) => void)[]> = new Map();

  constructor(config: { ndk: NDK; walletPubkey: string; secret: string }) {
    this.ndk = config.ndk;
    this.walletPubkey = config.walletPubkey;
    this.secret = config.secret;
  }

  async connect(): Promise<void> {
    // Implémentation de la connexion
  }

  async disconnect(): Promise<void> {
    // Implémentation de la déconnexion
  }

  async request(request: NWCRequest): Promise<NWCResponse> {
    // Implémentation de la requête
    return { result: null };
  }

  on(event: string, callback: (data: any) => void): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event)?.push(callback);
  }

  off(event: string, callback: (data: any) => void): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      const index = handlers.indexOf(callback);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }
}

export interface NWCConfig {
  relayUrl: string;
  walletPubkey: string;
  secret: string;
}

export class NWCService {
  private ndk: NDK;
  private nwc: NWC;
  private config: NWCConfig;

  constructor(config: NWCConfig) {
    this.config = config;
    this.ndk = new NDK({
      explicitRelayUrls: [config.relayUrl],
    });
    this.nwc = new NWC({
      ndk: this.ndk,
      walletPubkey: config.walletPubkey,
      secret: config.secret,
    });
  }

  async connect(): Promise<void> {
    try {
      await this.ndk.connect();
      await this.nwc.connect();
    } catch (error) {
      console.error("Erreur de connexion NWC:", error);
      throw error;
    }
  }

  async disconnect(): Promise<void> {
    try {
      await this.nwc.disconnect();
    } catch (error) {
      console.error("Erreur de déconnexion NWC:", error);
      throw error;
    }
  }

  async getBalance(): Promise<number> {
    try {
      const response = await this.nwc.request({
        method: "get_balance",
        params: {},
      });
      return response.result as number;
    } catch (error) {
      console.error("Erreur lors de la récupération du solde:", error);
      throw error;
    }
  }

  async createInvoice(amount: number, memo?: string): Promise<string> {
    try {
      const response = await this.nwc.request({
        method: "create_invoice",
        params: {
          amount,
          memo,
        },
      });
      return response.result as string;
    } catch (error) {
      console.error("Erreur lors de la création de la facture:", error);
      throw error;
    }
  }

  async payInvoice(invoice: string): Promise<string> {
    try {
      const response = await this.nwc.request({
        method: "pay_invoice",
        params: {
          invoice,
        },
      });
      return response.result as string;
    } catch (error) {
      console.error("Erreur lors du paiement de la facture:", error);
      throw error;
    }
  }

  async getChannels(): Promise<Channel[]> {
    try {
      const response = await this.nwc.request({
        method: "list_channels",
        params: {},
      });
      return response.result as Channel[];
    } catch (err) {
      const error =
        err instanceof Error
          ? err
          : new Error("Une erreur inconnue s'est produite");
      console.error("Erreur lors de la récupération des canaux:", error);
      throw error;
    }
  }

  async openChannel(nodeId: string, amount: number): Promise<string> {
    try {
      const response = await this.nwc.request({
        method: "open_channel",
        params: {
          nodeId,
          amount,
        },
      });
      return response.result as string;
    } catch (error) {
      console.error("Erreur lors de l'ouverture du canal:", error);
      throw error;
    }
  }

  async closeChannel(channelId: string): Promise<string> {
    try {
      const response = await this.nwc.request({
        method: "close_channel",
        params: {
          channelId,
        },
      });
      return response.result as string;
    } catch (error) {
      console.error("Erreur lors de la fermeture du canal:", error);
      throw error;
    }
  }

  on(event: string, callback: (data: any) => void): void {
    this.nwc.on(event, callback);
  }

  off(event: string, callback: (data: any) => void): void {
    this.nwc.off(event, callback);
  }
}
