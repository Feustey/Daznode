'use client';

import { useNode } from '@/lib/contexts/NodeContext';
import NodeHeader from './NodeHeader';
import StatsGrid from './StatsGrid';
import NodeIdentifiers from './NodeIdentifiers';
import RankingsSection from './RankingsSection';
import HistoricalCharts from './HistoricalCharts';
import LoadingSpinner from './LoadingSpinner';
import LiveIndicator from './LiveIndicator';
import { useWebSocketData } from '@/lib/websocket/useWebSocketData';

interface NodeDashboardProps {
  pubkey: string;
}

export default function NodeDashboard({ pubkey }: NodeDashboardProps) {
  const { nodeData, isLoading, isError, refreshData, lastUpdate, addFavorite, removeFavorite, favorites } = useNode();
  
  // Initialiser la connexion WebSocket (désactivée en développement)
  const { isConnected } = useWebSocketData({
    url: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws',
    pubkey,
    enabled: false // Activer en production avec les vrais endpoints
  });

  if (isLoading) return <LoadingSpinner />;
  if (isError) return <div className="p-6 text-red-500">Erreur lors du chargement des données</div>;
  if (!nodeData) return <div className="p-6">Aucune donnée disponible</div>;

  const handleToggleFavorite = () => {
    if (favorites.includes(pubkey)) {
      removeFavorite(pubkey);
    } else {
      addFavorite(pubkey);
    }
  };

  const isFavorite = favorites.includes(pubkey);

  return (
    <div className="container mx-auto">
      <div className="p-4 flex justify-between items-center">
        <LiveIndicator 
          lastUpdate={lastUpdate} 
          isLive={isConnected} 
        />
        <button 
          onClick={refreshData}
          className="bg-accent-blue text-white px-3 py-1 rounded text-sm hover:bg-blue-600 transition-colors"
        >
          Rafraîchir
        </button>
      </div>
      
      <NodeHeader 
        nodeData={nodeData} 
        onToggleFavorite={handleToggleFavorite}
        isFavorite={isFavorite}
      />
      
      <StatsGrid 
        nodeData={nodeData} 
      />
      
      <div className="p-6">
        <NodeIdentifiers nodeData={nodeData} />
      </div>
      
      <div className="p-6">
        <RankingsSection nodeData={nodeData} />
      </div>
      
      <div className="p-6">
        <HistoricalCharts nodeData={nodeData} />
      </div>
    </div>
  );
} 