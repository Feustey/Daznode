'use client';

import { useEffect, useState } from 'react';
import { MCPService } from '@/lib/mcp';
import { useNode } from '@/lib/contexts/NodeContext';
import { formatNumber, formatSats } from '@/lib/utils/formatters';

interface PotentialPeer {
  pubkey: string;
  alias: string;
  connectivityScore: number;
  revenueOpportunity: number;
  reliability: number;
  overallScore: number;
  centralityRank: number | null;
  recommended: boolean;
}

export default function PotentialPeersRanking() {
  const { pubkey } = useNode();
  const [loading, setLoading] = useState<boolean>(true);
  const [peers, setPeers] = useState<PotentialPeer[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        if (!pubkey) {
          throw new Error("Clé publique non disponible");
        }
        
        const mcpService = new MCPService();
        
        // En réalité, il faudrait avoir un endpoint API spécifique pour cette fonctionnalité
        // Pour la démo, nous allons simuler l'analyse en utilisant les données du réseau
        const nodeDetails = await mcpService.get_node_details(pubkey);
        const networkStats = await mcpService.get_network_stats();
        
        if (nodeDetails && networkStats) {
          // Récupérer des nœuds du réseau (en pratique, on filtrerait ceux pertinents)
          const networkNodes = await mcpService.get_network_nodes(50);
          
          // Exclure notre propre nœud et ceux déjà connectés
          const myConnectedPeers = nodeDetails.connected_peers || [];
          
          // Filtrer les nœuds potentiels
          const potentialPeers = networkNodes
            .filter((node: any) => 
              node.pubkey !== pubkey && 
              !myConnectedPeers.includes(node.pubkey))
            .map((node: any) => {
              // Calculer des scores simulés pour chaque nœud
              // En pratique, ces scores seraient basés sur des algorithmes plus complexes
              
              // Score de connectivité basé sur le nombre de canaux
              const connectivityScore = Math.min(1, (node.num_channels || 0) / 100) * 10;
              
              // Opportunité de revenus basée sur le volume routé
              const revenueOpportunity = Math.min(1, (node.routing_volume || 0) / 10000000) * 10;
              
              // Fiabilité basée sur le temps de fonctionnement
              const reliability = Math.min(1, (node.uptime || 0) / 0.95) * 10;
              
              // Score global (moyenne pondérée)
              const overallScore = (
                connectivityScore * 0.4 + 
                revenueOpportunity * 0.4 + 
                reliability * 0.2
              );
              
              // Déterminer si le nœud est recommandé
              const recommended = overallScore > 7.5;
              
              return {
                pubkey: node.pubkey,
                alias: node.alias || `Nœud ${node.pubkey.substring(0, 8)}`,
                connectivityScore,
                revenueOpportunity,
                reliability,
                overallScore,
                centralityRank: node.centrality_rank,
                recommended
              };
            });
          
          // Trier par score global
          const sortedPeers = potentialPeers.sort((a: PotentialPeer, b: PotentialPeer) => b.overallScore - a.overallScore);
          
          setPeers(sortedPeers);
        }
      } catch (error) {
        console.error('Erreur lors de la récupération des nœuds pairs potentiels:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [pubkey]);

  const renderScoreBar = (score: number) => {
    // Déterminer la couleur en fonction du score
    let color = 'bg-green-500';
    if (score < 5) color = 'bg-red-500';
    else if (score < 7.5) color = 'bg-yellow-500';
    
    return (
      <div className="w-full bg-gray-700 rounded-full h-1.5">
        <div
          className={`${color} h-1.5 rounded-full`}
          style={{ width: `${Math.min(100, Math.max(0, score * 10))}%` }}
        ></div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (peers.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        Aucun nœud pair potentiel trouvé
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <p className="text-gray-300 text-sm mb-4">
        Le tableau ci-dessous présente les nœuds pairs potentiels les plus intéressants pour votre nœud, 
        classés selon leur score global. Ces recommandations sont basées sur la connectivité, les opportunités 
        de revenus et la fiabilité de chaque nœud.
      </p>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-left text-gray-400 border-b border-gray-700">
              <th className="px-4 py-2 text-xs">Nœud</th>
              <th className="px-4 py-2 text-xs text-center">Score global</th>
              <th className="px-4 py-2 text-xs text-center">Connectivité</th>
              <th className="px-4 py-2 text-xs text-center">Potentiel de revenus</th>
              <th className="px-4 py-2 text-xs text-center">Fiabilité</th>
              <th className="px-4 py-2 text-xs text-center">Recommandé</th>
            </tr>
          </thead>
          <tbody>
            {peers.map(peer => (
              <tr key={peer.pubkey} className="border-b border-gray-700">
                <td className="px-4 py-3">
                  <div className="flex flex-col">
                    <span className="font-medium text-white">{peer.alias}</span>
                    <span className="text-xs text-gray-400">{peer.pubkey.substring(0, 16)}...</span>
                    {peer.centralityRank && (
                      <span className="text-xs text-blue-400">Rang centralité: #{peer.centralityRank}</span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3 text-center">
                  <div className="flex flex-col items-center">
                    <span className="font-bold text-white">{peer.overallScore.toFixed(1)}</span>
                    {renderScoreBar(peer.overallScore)}
                  </div>
                </td>
                <td className="px-4 py-3 text-center">
                  <div className="flex flex-col items-center">
                    <span className="text-sm text-white">{peer.connectivityScore.toFixed(1)}</span>
                    {renderScoreBar(peer.connectivityScore)}
                  </div>
                </td>
                <td className="px-4 py-3 text-center">
                  <div className="flex flex-col items-center">
                    <span className="text-sm text-white">{peer.revenueOpportunity.toFixed(1)}</span>
                    {renderScoreBar(peer.revenueOpportunity)}
                  </div>
                </td>
                <td className="px-4 py-3 text-center">
                  <div className="flex flex-col items-center">
                    <span className="text-sm text-white">{peer.reliability.toFixed(1)}</span>
                    {renderScoreBar(peer.reliability)}
                  </div>
                </td>
                <td className="px-4 py-3 text-center">
                  {peer.recommended ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Recommandé
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      Potentiel
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      <div className="bg-gray-800 p-4 rounded-lg">
        <h4 className="text-lg font-semibold mb-2 text-white">Méthodologie de notation</h4>
        <ul className="space-y-2 text-sm text-gray-300">
          <li><strong className="text-blue-400">Connectivité</strong>: Mesure la qualité du nœud en tant que hub dans le réseau, basée sur le nombre et la qualité de ses canaux.</li>
          <li><strong className="text-blue-400">Potentiel de revenus</strong>: Estimation des revenus potentiels basée sur le volume de routage historique du nœud.</li>
          <li><strong className="text-blue-400">Fiabilité</strong>: Évaluation de la stabilité et de la disponibilité du nœud dans le temps.</li>
          <li><strong className="text-blue-400">Score global</strong>: Moyenne pondérée des trois métriques précédentes (40% connectivité, 40% revenus, 20% fiabilité).</li>
        </ul>
      </div>
    </div>
  );
} 