"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { MoveUp, Zap, Activity, Coins, TrendingUp, Anchor } from "lucide-react";
import { MCPService } from "@/lib/mcp";
import { formatNumber, formatSats } from "@/lib/utils/formatters";

interface NetworkStats {
  network_summary: {
    total_nodes: number;
    active_nodes: number;
    total_channels: number;
    active_channels: number;
    total_capacity: number;
  };
  daily_volume: number;
  monitored_channels: number;
  revenue_growth: number;
  avg_channel_size: number;
  network_liquidity_index: number;
}

export default function Hero() {
  const [stats, setStats] = useState<NetworkStats | null>(null);
  const [loading, setLoading] = useState(true);
  const mcpService = new MCPService();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        
        // Récupérer les statistiques réseau depuis MCP
        const mcpNetworkStats = await mcpService.get_network_stats();
        
        // Récupérer les performances de canaux pour le volume quotidien
        const channelPerformance = await mcpService.get_channels_performance("day");
        
        // Fusionner les données avec les statistiques de l'API locale
        const response = await fetch('/api/network/stats');
        const apiData = response.ok ? await response.json() : {};
        
        setStats({
          network_summary: {
            total_nodes: mcpNetworkStats.num_nodes || 0,
            active_nodes: mcpNetworkStats.active_nodes || 0,
            total_channels: mcpNetworkStats.num_channels || 0,
            active_channels: mcpNetworkStats.active_channels || 0,
            total_capacity: mcpNetworkStats.total_capacity || 0,
          },
          daily_volume: channelPerformance.total_volume || apiData.daily_volume || 450000000,
          monitored_channels: apiData.monitored_channels || 50000,
          revenue_growth: apiData.revenue_growth || 12.5,
          avg_channel_size: mcpNetworkStats.avg_capacity_per_channel || 0,
          network_liquidity_index: channelPerformance.liquidity_index || 0.75,
        });
      } catch (error) {
        console.error('Failed to fetch network stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  // Statistiques par défaut au cas où l'API échoue
  const defaultStats = {
    monitored_channels: 50000,
    daily_volume: 450000000,
    active_nodes: 17500,
    revenue_growth: 12.5,
    avg_channel_size: 2500000,
    network_liquidity_index: 0.75
  };

  // Métriques à afficher (ajout de deux nouvelles métriques MCP)
  const statItems = [
    {
      label: "Canaux monitorés",
      value: stats?.monitored_channels || defaultStats.monitored_channels,
      icon: <Activity className="w-6 h-6 text-blue-400" />,
      formatter: formatNumber
    },
    {
      label: "Volume quotidien",
      value: stats?.daily_volume || defaultStats.daily_volume,
      icon: <Zap className="w-6 h-6 text-yellow-400" />,
      formatter: (val: number) => formatSats(val)
    },
    {
      label: "Nœuds actifs",
      value: stats?.network_summary?.active_nodes || defaultStats.active_nodes,
      icon: <Coins className="w-6 h-6 text-purple-400" />,
      formatter: formatNumber
    },
    {
      label: "Croissance revenus",
      value: stats?.revenue_growth || defaultStats.revenue_growth,
      icon: <MoveUp className="w-6 h-6 text-green-400" />,
      formatter: (val: number) => `+${val}%`
    },
    {
      label: "Taille moyenne canaux",
      value: stats?.avg_channel_size || defaultStats.avg_channel_size,
      icon: <TrendingUp className="w-6 h-6 text-orange-400" />,
      formatter: formatSats
    },
    {
      label: "Liquidité réseau",
      value: stats?.network_liquidity_index || defaultStats.network_liquidity_index,
      icon: <Anchor className="w-6 h-6 text-teal-400" />,
      formatter: (val: number) => `${(val * 100).toFixed(1)}%`
    }
  ];

  return (
    <div className="relative min-h-[80vh] flex items-center justify-center bg-gradient-to-br from-blue-900 via-purple-900 to-purple-950">
      <div className="container mx-auto px-4 text-center">
        <h1 className="text-6xl font-bold mb-6 bg-gradient-to-r from-blue-400 via-purple-400 to-coral-400 bg-clip-text text-transparent">
          Daznode
        </h1>
        <p className="text-2xl text-gray-200 mb-8 max-w-3xl mx-auto">
          Tableau de bord intelligent pour optimiser votre nœud Lightning Network
        </p>

        <div className="flex gap-4 justify-center">
          <button className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-md text-lg">
            <Link href="/overview">
              Découvrir →
            </Link>
          </button>
          <button className="bg-gray-700 hover:bg-gray-600 text-white font-semibold py-3 px-6 rounded-md text-lg">
            <Link href="/trends">
              Explorer les tendances
            </Link>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-20">
          {statItems.map((item, index) => (
            <div key={index} className="bg-opacity-20 bg-blue-900 p-6 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                {item.icon}
                <h3 className="text-xl font-bold text-blue-400">{item.label}</h3>
              </div>
              <p className="text-4xl font-bold">
                {loading ? (
                  <span className="animate-pulse bg-blue-400/20 h-10 w-24 inline-block rounded"></span>
                ) : (
                  item.formatter(item.value)
                )}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 