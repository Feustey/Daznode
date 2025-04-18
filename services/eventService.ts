import { mcpService } from "./mcpService";

export interface NodeEvent {
  id: string;
  nodeId: string;
  type:
    | "channel_opened"
    | "channel_closed"
    | "payment_sent"
    | "payment_received";
  data: any;
  timestamp: Date;
}

export interface ChannelEvent {
  id: string;
  channelId: string;
  type: "payment_sent" | "payment_received" | "capacity_changed";
  data: any;
  timestamp: Date;
}

export class EventService {
  private nodeEventSubscriptions: Map<string, (event: NodeEvent) => void> =
    new Map();
  private channelEventSubscriptions: Map<
    string,
    (event: ChannelEvent) => void
  > = new Map();

  // S'abonner aux événements d'un nœud
  async subscribeToNodeEvents(
    nodeId: string,
    callback: (event: NodeEvent) => void
  ): Promise<string> {
    try {
      // Utiliser MCP pour s'abonner aux événements d'un nœud
      mcpService.subscribeToNodeEvents(nodeId, (event: any) => {
        const nodeEvent: NodeEvent = {
          id: event.id,
          nodeId,
          type: event.type,
          data: event.data,
          timestamp: new Date(event.timestamp),
        };
        callback(nodeEvent);
      });

      const subscriptionId = `node_${nodeId}_${Date.now()}`;
      this.nodeEventSubscriptions.set(subscriptionId, callback);

      return subscriptionId;
    } catch (error) {
      console.error("Error subscribing to node events with MCP:", error);
      throw error;
    }
  }

  // S'abonner aux événements d'un canal
  async subscribeToChannelEvents(
    channelId: string,
    callback: (event: ChannelEvent) => void
  ): Promise<string> {
    try {
      // Utiliser MCP pour s'abonner aux événements d'un canal
      mcpService.subscribeToChannelEvents(channelId, (event: any) => {
        const channelEvent: ChannelEvent = {
          id: event.id,
          channelId,
          type: event.type,
          data: event.data,
          timestamp: new Date(event.timestamp),
        };
        callback(channelEvent);
      });

      const subscriptionId = `channel_${channelId}_${Date.now()}`;
      this.channelEventSubscriptions.set(subscriptionId, callback);

      return subscriptionId;
    } catch (error) {
      console.error("Error subscribing to channel events with MCP:", error);
      throw error;
    }
  }

  // Se désabonner des événements d'un nœud
  async unsubscribeFromNodeEvents(subscriptionId: string): Promise<boolean> {
    try {
      // Supprimer la référence à la fonction de callback
      this.nodeEventSubscriptions.delete(subscriptionId);
      return true;
    } catch (error) {
      console.error("Error unsubscribing from node events:", error);
      return false;
    }
  }

  // Se désabonner des événements d'un canal
  async unsubscribeFromChannelEvents(subscriptionId: string): Promise<boolean> {
    try {
      // Supprimer la référence à la fonction de callback
      this.channelEventSubscriptions.delete(subscriptionId);
      return true;
    } catch (error) {
      console.error("Error unsubscribing from channel events:", error);
      return false;
    }
  }
}

export const eventService = new EventService();
