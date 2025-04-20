'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { NodeData } from '@/lib/types/node';
import { getNodeData } from '@/lib/api/nodeApi';

// Définir le pubkey par défaut de Feustey
const DEFAULT_PUBKEY = '02778f4a4eb3a2344b9fd8ee72e7ec5f03f803e5f5273e2e1a2af508910cf2b12b';

interface NodeContextType {
  pubkey: string;
  setPubkey: (pubkey: string) => void;
  nodeData: NodeData | null;
  isLoading: boolean;
  isError: boolean;
  refreshData: () => void;
  favorites: string[];
  addFavorite: (pubkey: string) => void;
  removeFavorite: (pubkey: string) => void;
  lastUpdate: Date | null;
}

const NodeContext = createContext<NodeContextType | undefined>(undefined);

interface NodeProviderProps {
  children: ReactNode;
}

export const NodeProvider = ({ children }: NodeProviderProps) => {
  const [pubkey, setPubkey] = useState<string>(DEFAULT_PUBKEY);
  const [nodeData, setNodeData] = useState<NodeData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [favorites, setFavorites] = useState<string[]>([]);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // Récupérer les favoris depuis le localStorage au chargement
  useEffect(() => {
    const storedFavorites = localStorage.getItem('daznode_favorites');
    if (storedFavorites) {
      try {
        const parsedFavorites = JSON.parse(storedFavorites) as string[];
        setFavorites(parsedFavorites);
      } catch (error) {
        console.error('Erreur lors de la lecture des favoris:', error);
        setFavorites([]);
      }
    }
  }, []);

  // Mettre à jour les favoris dans le localStorage
  useEffect(() => {
    try {
      localStorage.setItem('daznode_favorites', JSON.stringify(favorites));
    } catch (error) {
      console.error('Erreur lors de la sauvegarde des favoris:', error);
    }
  }, [favorites]);

  // Charger les données du nœud
  const fetchNodeData = async () => {
    try {
      setIsLoading(true);
      setIsError(false);
      const data = await getNodeData(pubkey);
      setNodeData(data);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Erreur lors de la récupération des données du nœud:', error);
      setIsError(true);
    } finally {
      setIsLoading(false);
    }
  };

  // Charger les données au chargement et lorsque le pubkey change
  useEffect(() => {
    fetchNodeData();
    
    const intervalId = setInterval(fetchNodeData, 60000);
    
    return () => clearInterval(intervalId);
  }, [pubkey]);

  // Forcer un rechargement des données
  const refreshData = () => {
    fetchNodeData();
  };

  // Ajouter un nœud aux favoris
  const addFavorite = (nodePubkey: string) => {
    if (!favorites.includes(nodePubkey)) {
      setFavorites([...favorites, nodePubkey]);
    }
  };

  // Retirer un nœud des favoris
  const removeFavorite = (nodePubkey: string) => {
    setFavorites(favorites.filter(pk => pk !== nodePubkey));
  };

  const value = {
    pubkey,
    setPubkey,
    nodeData,
    isLoading,
    isError,
    refreshData,
    favorites,
    addFavorite,
    removeFavorite,
    lastUpdate
  };

  return <NodeContext.Provider value={value}>{children}</NodeContext.Provider>;
};

export const useNode = (): NodeContextType => {
  const context = useContext(NodeContext);
  if (context === undefined) {
    throw new Error('useNode doit être utilisé au sein d\'un NodeProvider');
  }
  return context;
}; 