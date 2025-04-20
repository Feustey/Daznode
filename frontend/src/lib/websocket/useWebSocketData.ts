'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { NodeData } from '@/lib/types/node';

interface WebSocketMessage {
  type: string;
  data: unknown;
}

interface UseWebSocketOptions {
  url: string;
  pubkey: string;
  enabled?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  liveData: NodeData | null;
  lastUpdate: Date | null;
  error: Error | null;
  sendMessage: (type: string, data: unknown) => void;
  reconnect: () => void;
}

export const useWebSocketData = ({
  url,
  pubkey,
  enabled = true,
  reconnectInterval = 3000,
  maxReconnectAttempts = 5
}: UseWebSocketOptions): UseWebSocketReturn => {
  const [isConnected, setIsConnected] = useState(false);
  const [liveData, setLiveData] = useState<NodeData | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [error, setError] = useState<Error | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Fonction pour établir une connexion WebSocket
  const connect = useCallback(() => {
    if (!enabled) return;
    
    // Nettoyer toute connexion existante
    if (wsRef.current) {
      wsRef.current.close();
    }
    
    try {
      // Établir une nouvelle connexion
      const fullUrl = `${url}?pubkey=${pubkey}`;
      const ws = new WebSocket(fullUrl);
      
      ws.onopen = () => {
        console.log('WebSocket connecté');
        setIsConnected(true);
        reconnectAttemptsRef.current = 0; // Réinitialiser le compteur de tentatives
        setError(null);
      };
      
      ws.onmessage = (event: MessageEvent) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          
          if (message.type === 'node_update') {
            setLiveData(message.data as NodeData);
            setLastUpdate(new Date());
          }
        } catch (err) {
          console.error('Erreur lors du traitement du message WebSocket:', err);
          setError(err instanceof Error ? err : new Error('Erreur inconnue'));
        }
      };
      
      ws.onerror = (event: Event) => {
        console.error('Erreur WebSocket:', event);
        setError(new Error('Erreur de connexion WebSocket'));
      };
      
      ws.onclose = () => {
        console.log('WebSocket déconnecté');
        setIsConnected(false);
        
        // Tenter de se reconnecter
        if (enabled && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1;
          
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`Tentative de reconnexion (${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`);
            connect();
          }, reconnectInterval);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          setError(new Error(`Échec de connexion après ${maxReconnectAttempts} tentatives`));
        }
      };
      
      wsRef.current = ws;
    } catch (err) {
      console.error('Erreur lors de la création de la connexion WebSocket:', err);
      setError(err instanceof Error ? err : new Error('Erreur inconnue'));
    }
  }, [url, pubkey, enabled, reconnectInterval, maxReconnectAttempts]);

  // Établir la connexion au montage ou lorsque les dépendances changent
  useEffect(() => {
    connect();
    
    // Nettoyer lors du démontage
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  // Fonction pour envoyer un message
  const sendMessage = useCallback((type: string, data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const message: WebSocketMessage = { type, data };
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('Tentative d\'envoi d\'un message sur une connexion fermée');
    }
  }, []);

  // Fonction pour forcer une reconnexion
  const reconnect = useCallback(() => {
    reconnectAttemptsRef.current = 0;
    connect();
  }, [connect]);

  return {
    isConnected,
    liveData,
    lastUpdate,
    error,
    sendMessage,
    reconnect
  };
}; 