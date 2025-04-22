'use client';

import { useEffect, useState } from 'react';
import { MCPService } from '@/lib/mcp';
import { useNode } from '@/lib/contexts/NodeContext';
import { formatNumber, formatSats } from '@/lib/utils/formatters';

interface NodeData {
  pubkey: string;
  alias: string;
  num_channels: number;
  capacity: number;
  avg_capacity: number;
  avg_fee_rate: number;
  routing_volume_30d: number;
  uptime: number;
  centrality: number;
  rank: number;
  score: number;
}

interface ComparisonData {
  yourNode: NodeData | null;
  similarNodes: NodeData[];
  topNodes: NodeData[];
}

export default function NodeComparison() {
  const { pubkey } = useNode();
  const [loading, setLoading] = useState<boolean>(true);
  const [data, setData] = useState<ComparisonData | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        if (!pubkey) {
          throw new Error("Clé publique non disponible");
        }
        
        const mcpService = new MCPService();
        
        // Obtenir les détails du nœud actuel
        const nodeDetails = await mcpService.get_node_details(pubkey);
        
        // Obtenir le classement du nœud
        const nodeRanking = await mcpService.get_node_ranking(pubkey);
        
        if (nodeDetails && nodeRanking) {
          const yourNode = {
            pubkey: nodeDetails.pubkey,
            alias: nodeDetails.alias,
            num_channels: nodeDetails.num_channels,
            capacity: nodeDetails.capacity,
            avg_capacity: nodeDetails.avg_channel_capacity,
            avg_fee_rate: nodeDetails.avg_fee_rate,
            routing_volume_30d: nodeDetails.routing_volume_30d,
            uptime: nodeDetails.uptime,
            centrality: nodeRanking.centrality,
            rank: nodeRanking.rank,
            score: nodeRanking.score,
          };
          
          // Les nœuds similaires (généralement dans la même plage de classement)
          const similarNodes = nodeRanking.similar_nodes || [];
          
          // Les nœuds de référence (top performers)
          const topNodes = nodeRanking.top_nodes || [];
          
          setData({
            yourNode,
            similarNodes: similarNodes.slice(0, 5),
            topNodes: topNodes.slice(0, 5),
          });
        }
      } catch (error) {
        console.error('Erreur lors de la récupération des données de comparaison:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [pubkey]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!data || !data.yourNode) {
    return (
      <div className="text-center py-12 text-gray-400">
        Impossible de charger les données de comparaison
      </div>
    );
  }

  const renderNodeRow = (node: NodeData) => (
    <tr key={node.pubkey} className="border-t border-gray-700">
      <td className="px-4 py-2 text-sm">{node.alias || node.pubkey.substring(0, 8)}</td>
      <td className="px-4 py-2 text-sm text-right">{node.num_channels}</td>
      <td className="px-4 py-2 text-sm text-right">{formatSats(node.capacity)}</td>
      <td className="px-4 py-2 text-sm text-right">{formatNumber(Math.round(node.routing_volume_30d / 1000))}k</td>
      <td className="px-4 py-2 text-sm text-right">{node.avg_fee_rate ? `${node.avg_fee_rate} ppm` : 'N/A'}</td>
      <td className="px-4 py-2 text-sm text-right">{node.rank ? `#${node.rank}` : 'N/A'}</td>
    </tr>
  );

  return (
    <div className="space-y-6">
      <div className="bg-blue-900 bg-opacity-30 rounded-lg p-4 border border-blue-500">
        <h3 className="text-lg font-semibold mb-3 text-blue-300">Votre nœud</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-xs text-gray-400">Capacité totale</p>
            <p className="text-2xl font-bold">{formatSats(data.yourNode.capacity)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400">Nombre de canaux</p>
            <p className="text-2xl font-bold">{data.yourNode.num_channels}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400">Volume routé (30j)</p>
            <p className="text-2xl font-bold">{formatSats(data.yourNode.routing_volume_30d)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400">Classement</p>
            <p className="text-2xl font-bold">#{data.yourNode.rank || 'N/A'}</p>
          </div>
        </div>
      </div>
      
      <div className="bg-gray-800 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-3 text-purple-400">Nœuds similaires</h3>
        <table className="w-full">
          <thead>
            <tr className="text-left text-gray-400">
              <th className="px-4 py-2 text-xs">Alias</th>
              <th className="px-4 py-2 text-xs text-right">Canaux</th>
              <th className="px-4 py-2 text-xs text-right">Capacité</th>
              <th className="px-4 py-2 text-xs text-right">Vol. routé (k)</th>
              <th className="px-4 py-2 text-xs text-right">Frais moy.</th>
              <th className="px-4 py-2 text-xs text-right">Rang</th>
            </tr>
          </thead>
          <tbody>
            {data.similarNodes.length > 0 ? (
              data.similarNodes.map(renderNodeRow)
            ) : (
              <tr>
                <td colSpan={6} className="px-4 py-4 text-center text-sm text-gray-500">
                  Aucun nœud similaire trouvé
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      
      <div className="bg-gray-800 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-3 text-yellow-400">Nœuds de référence</h3>
        <table className="w-full">
          <thead>
            <tr className="text-left text-gray-400">
              <th className="px-4 py-2 text-xs">Alias</th>
              <th className="px-4 py-2 text-xs text-right">Canaux</th>
              <th className="px-4 py-2 text-xs text-right">Capacité</th>
              <th className="px-4 py-2 text-xs text-right">Vol. routé (k)</th>
              <th className="px-4 py-2 text-xs text-right">Frais moy.</th>
              <th className="px-4 py-2 text-xs text-right">Rang</th>
            </tr>
          </thead>
          <tbody>
            {data.topNodes.length > 0 ? (
              data.topNodes.map(renderNodeRow)
            ) : (
              <tr>
                <td colSpan={6} className="px-4 py-4 text-center text-sm text-gray-500">
                  Aucun nœud de référence trouvé
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
} 