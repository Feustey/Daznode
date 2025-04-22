'use client';

import { useEffect, useState } from 'react';
import { MCPService } from '@/lib/mcp';
import { formatSats } from '@/lib/utils/formatters';

interface ChannelProfitabilityProps {
  timeframe: string;
}

interface Channel {
  id: string;
  alias: string;
  profit: number;
  volume: number;
  routingCount: number;
  fee: number;
}

interface ProfitabilityMatrix {
  highProfit: Channel[];
  mediumProfit: Channel[];
  lowProfit: Channel[];
  negative: Channel[];
}

export default function ChannelProfitability({ timeframe }: ChannelProfitabilityProps) {
  const [loading, setLoading] = useState<boolean>(true);
  const [matrix, setMatrix] = useState<ProfitabilityMatrix | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const mcpService = new MCPService();
        const response = await mcpService.get_channels_performance(timeframe);
        
        if (response && response.channels) {
          const channels = response.channels;
          
          // Tri des canaux par profit
          const sortedChannels = [...channels].sort((a, b) => b.profit - a.profit);
          
          // Classification des canaux
          const highProfit = sortedChannels.filter(channel => channel.profit > 1000);
          const mediumProfit = sortedChannels.filter(channel => channel.profit > 100 && channel.profit <= 1000);
          const lowProfit = sortedChannels.filter(channel => channel.profit > 0 && channel.profit <= 100);
          const negative = sortedChannels.filter(channel => channel.profit <= 0);
          
          setMatrix({
            highProfit: highProfit.slice(0, 5),
            mediumProfit: mediumProfit.slice(0, 5),
            lowProfit: lowProfit.slice(0, 5),
            negative: negative.slice(0, 5)
          });
        }
      } catch (error) {
        console.error('Erreur lors de la récupération des performances des canaux:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [timeframe]);

  const renderChannelRow = (channel: Channel) => (
    <tr key={channel.id} className="border-t border-gray-700">
      <td className="px-4 py-2 text-sm">{channel.alias || channel.id.substring(0, 8)}</td>
      <td className="px-4 py-2 text-sm text-right">{formatSats(channel.profit)}</td>
      <td className="px-4 py-2 text-sm text-right">{formatSats(channel.volume || 0)}</td>
      <td className="px-4 py-2 text-sm text-right">{channel.routingCount || 0}</td>
      <td className="px-4 py-2 text-sm text-right">{channel.fee ? channel.fee + ' ppm' : 'N/A'}</td>
    </tr>
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!matrix) {
    return (
      <div className="text-center py-12 text-gray-400">
        Aucune donnée de canal disponible pour la période sélectionnée
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-3 text-green-400">Profits élevés (&gt;1000 sats)</h3>
          <table className="w-full">
            <thead>
              <tr className="text-left text-gray-400">
                <th className="px-4 py-2 text-xs">Canal</th>
                <th className="px-4 py-2 text-xs text-right">Profit</th>
                <th className="px-4 py-2 text-xs text-right">Volume</th>
                <th className="px-4 py-2 text-xs text-right">Routages</th>
                <th className="px-4 py-2 text-xs text-right">Frais</th>
              </tr>
            </thead>
            <tbody>
              {matrix.highProfit.length > 0 ? (
                matrix.highProfit.map(renderChannelRow)
              ) : (
                <tr>
                  <td colSpan={5} className="px-4 py-4 text-center text-sm text-gray-500">
                    Aucun canal dans cette catégorie
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-3 text-blue-400">Profits moyens (100-1000 sats)</h3>
          <table className="w-full">
            <thead>
              <tr className="text-left text-gray-400">
                <th className="px-4 py-2 text-xs">Canal</th>
                <th className="px-4 py-2 text-xs text-right">Profit</th>
                <th className="px-4 py-2 text-xs text-right">Volume</th>
                <th className="px-4 py-2 text-xs text-right">Routages</th>
                <th className="px-4 py-2 text-xs text-right">Frais</th>
              </tr>
            </thead>
            <tbody>
              {matrix.mediumProfit.length > 0 ? (
                matrix.mediumProfit.map(renderChannelRow)
              ) : (
                <tr>
                  <td colSpan={5} className="px-4 py-4 text-center text-sm text-gray-500">
                    Aucun canal dans cette catégorie
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-3 text-yellow-400">Profits faibles (0-100 sats)</h3>
          <table className="w-full">
            <thead>
              <tr className="text-left text-gray-400">
                <th className="px-4 py-2 text-xs">Canal</th>
                <th className="px-4 py-2 text-xs text-right">Profit</th>
                <th className="px-4 py-2 text-xs text-right">Volume</th>
                <th className="px-4 py-2 text-xs text-right">Routages</th>
                <th className="px-4 py-2 text-xs text-right">Frais</th>
              </tr>
            </thead>
            <tbody>
              {matrix.lowProfit.length > 0 ? (
                matrix.lowProfit.map(renderChannelRow)
              ) : (
                <tr>
                  <td colSpan={5} className="px-4 py-4 text-center text-sm text-gray-500">
                    Aucun canal dans cette catégorie
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-3 text-red-400">Canaux non rentables (≤0 sats)</h3>
          <table className="w-full">
            <thead>
              <tr className="text-left text-gray-400">
                <th className="px-4 py-2 text-xs">Canal</th>
                <th className="px-4 py-2 text-xs text-right">Profit</th>
                <th className="px-4 py-2 text-xs text-right">Volume</th>
                <th className="px-4 py-2 text-xs text-right">Routages</th>
                <th className="px-4 py-2 text-xs text-right">Frais</th>
              </tr>
            </thead>
            <tbody>
              {matrix.negative.length > 0 ? (
                matrix.negative.map(renderChannelRow)
              ) : (
                <tr>
                  <td colSpan={5} className="px-4 py-4 text-center text-sm text-gray-500">
                    Aucun canal dans cette catégorie
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
} 