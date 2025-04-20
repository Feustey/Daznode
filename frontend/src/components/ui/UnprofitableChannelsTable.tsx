'use client';

import { useState, useEffect } from 'react';
import { MCPService } from '@/lib/mcp';

interface Channel {
  id: string;
  alias: string;
  routedOut: number;
  lastRouting: string;
  rebalancedOut: number;
  lastRebalance: string;
  profit: number;
  assistedRevenue: number;
  initiator: string;
  localRatio: number;
  stuckIndex: number;
}

export default function UnprofitableChannelsTable() {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [timeframe, setTimeframe] = useState('week');
  const [loading, setLoading] = useState(true);
  const [sortConfig, setSortConfig] = useState<{
    key: keyof Channel;
    direction: 'asc' | 'desc';
  }>({ key: 'stuckIndex', direction: 'desc' });

  useEffect(() => {
    const fetchChannels = async () => {
      try {
        setLoading(true);
        const mcpService = new MCPService();
        const data = await mcpService.get_channels_performance(timeframe);
        setChannels(data.channels);
      } catch (error) {
        console.error('Erreur lors de la récupération des canaux:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchChannels();
  }, [timeframe]);

  const handleSort = (key: keyof Channel) => {
    setSortConfig((prev) => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc',
    }));
  };

  const sortedChannels = [...channels].sort((a, b) => {
    if (sortConfig.direction === 'asc') {
      return a[sortConfig.key] > b[sortConfig.key] ? 1 : -1;
    }
    return a[sortConfig.key] < b[sortConfig.key] ? 1 : -1;
  });

  if (loading) {
    return <div>Chargement...</div>;
  }

  return (
    <div className="overflow-x-auto">
      <div className="mb-4">
        <label htmlFor="timeframe" className="mr-2">
          Période:
        </label>
        <select
          id="timeframe"
          value={timeframe}
          onChange={(e) => setTimeframe(e.target.value)}
          className="rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
        >
          <option value="week">7 jours</option>
          <option value="month">30 jours</option>
          <option value="quarter">90 jours</option>
        </select>
      </div>

      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
              onClick={() => handleSort('id')}
            >
              ID du canal
            </th>
            <th
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
              onClick={() => handleSort('alias')}
            >
              Alias
            </th>
            <th
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
              onClick={() => handleSort('routedOut')}
            >
              Routé sortant (sats)
            </th>
            <th
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
              onClick={() => handleSort('lastRouting')}
            >
              Dernier routage
            </th>
            <th
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
              onClick={() => handleSort('rebalancedOut')}
            >
              Rebalancé sortant (sats)
            </th>
            <th
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
              onClick={() => handleSort('lastRebalance')}
            >
              Dernier rebalancement
            </th>
            <th
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
              onClick={() => handleSort('profit')}
            >
              Profit
            </th>
            <th
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
              onClick={() => handleSort('assistedRevenue')}
            >
              Revenus assistés
            </th>
            <th
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
              onClick={() => handleSort('initiator')}
            >
              Initiateur
            </th>
            <th
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
              onClick={() => handleSort('localRatio')}
            >
              Ratio local
            </th>
            <th
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
              onClick={() => handleSort('stuckIndex')}
            >
              Index de blocage
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {sortedChannels.map((channel) => (
            <tr key={channel.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {channel.id}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {channel.alias}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {channel.routedOut.toLocaleString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {channel.lastRouting}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {channel.rebalancedOut.toLocaleString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {channel.lastRebalance}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {channel.profit.toLocaleString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {channel.assistedRevenue.toLocaleString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {channel.initiator}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {channel.localRatio}%
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {channel.stuckIndex}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 