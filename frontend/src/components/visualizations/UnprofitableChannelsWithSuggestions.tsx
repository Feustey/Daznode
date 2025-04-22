'use client';

import { useEffect, useState } from 'react';
import { MCPService } from '@/lib/mcp';
import { formatSats } from '@/lib/utils/formatters';

interface UnprofitableChannelsWithSuggestionsProps {
  timeframe: string;
}

interface Channel {
  id: string;
  alias: string;
  profit: number;
  stuckIndex: number;
  localRatio: number;
  suggestedAction: string;
  suggestedFee: number | null;
  lastActivity: string;
}

export default function UnprofitableChannelsWithSuggestions({ timeframe }: UnprofitableChannelsWithSuggestionsProps) {
  const [loading, setLoading] = useState<boolean>(true);
  const [channels, setChannels] = useState<Channel[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const mcpService = new MCPService();
        const response = await mcpService.get_channels_performance(timeframe);
        
        if (response && response.channels) {
          // Filtrer les canaux non rentables
          const unprofitableChannels = response.channels
            .filter((channel: any) => channel.profit < 0)
            .map((channel: any) => {
              let suggestedAction = '';
              let suggestedFee = null;
              
              // Logique de suggestion basée sur les métriques du canal
              if (channel.localRatio > 0.8) {
                suggestedAction = 'Équilibrer le canal (trop de fonds côté local)';
              } else if (channel.localRatio < 0.2) {
                suggestedAction = 'Équilibrer le canal (trop peu de fonds côté local)';
              } else if (channel.stuckIndex && channel.stuckIndex > 0.7) {
                suggestedAction = 'Réévaluer les frais (canal bloqué)';
                
                // Suggérer des frais basés sur la moyenne du réseau
                const currentFee = channel.fee || 0;
                suggestedFee = Math.round(currentFee * 1.5); // Augmenter de 50%
              } else if (channel.lastActivity && new Date(channel.lastActivity).getTime() < Date.now() - 30 * 24 * 60 * 60 * 1000) {
                suggestedAction = 'Considérer la fermeture (inactif)';
              } else {
                suggestedAction = 'Surveiller les performances';
              }
              
              return {
                ...channel,
                suggestedAction,
                suggestedFee,
              };
            });
          
          setChannels(unprofitableChannels);
        }
      } catch (error) {
        console.error('Erreur lors de la récupération des données de canaux:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [timeframe]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (channels.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        Aucun canal non rentable trouvé pour la période sélectionnée
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="text-left text-gray-400 border-b border-gray-700">
            <th className="px-4 py-2 text-xs">Canal</th>
            <th className="px-4 py-2 text-xs text-right">Profit</th>
            <th className="px-4 py-2 text-xs">Ratio local</th>
            <th className="px-4 py-2 text-xs">Dernière activité</th>
            <th className="px-4 py-2 text-xs">Action suggérée</th>
            <th className="px-4 py-2 text-xs text-right">Frais suggérés</th>
          </tr>
        </thead>
        <tbody>
          {channels.map(channel => (
            <tr key={channel.id} className="border-b border-gray-700">
              <td className="px-4 py-3">
                <div className="flex flex-col">
                  <span className="font-medium text-white">{channel.alias || 'Canal sans alias'}</span>
                  <span className="text-xs text-gray-400">{channel.id.substring(0, 12)}...</span>
                </div>
              </td>
              <td className="px-4 py-3 text-right text-red-400 font-medium">
                {formatSats(channel.profit)}
              </td>
              <td className="px-4 py-3">
                <div className="w-full bg-gray-700 rounded-full h-2.5">
                  <div
                    className="bg-blue-600 h-2.5 rounded-full"
                    style={{ width: `${Math.min(100, Math.max(0, channel.localRatio * 100))}%` }}
                  ></div>
                </div>
                <span className="text-xs text-gray-400">{Math.round(channel.localRatio * 100)}%</span>
              </td>
              <td className="px-4 py-3 text-sm text-gray-300">
                {channel.lastActivity ? new Date(channel.lastActivity).toLocaleDateString() : 'Inconnue'}
              </td>
              <td className="px-4 py-3 text-sm">
                {channel.suggestedAction}
              </td>
              <td className="px-4 py-3 text-right text-sm">
                {channel.suggestedFee ? `${channel.suggestedFee} ppm` : '-'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      
      <div className="mt-6 p-4 bg-yellow-900 bg-opacity-20 border border-yellow-700 rounded-md">
        <h4 className="text-yellow-500 text-sm font-medium mb-2">Comment interpréter ce tableau ?</h4>
        <ul className="text-xs text-gray-300 space-y-1 list-disc pl-4">
          <li>Les canaux sont classés par ordre de rentabilité (du moins rentable au plus rentable)</li>
          <li>Le ratio local indique la proportion de fonds sur votre côté du canal</li>
          <li>Les suggestions sont basées sur l'analyse des données de performance et sont indicatives</li>
          <li>Tenez compte du contexte global avant d'effectuer des changements (volume global du réseau, événements récents, etc.)</li>
        </ul>
      </div>
    </div>
  );
} 