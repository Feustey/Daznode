'use client';

import { useEffect, useState } from 'react';
import { MCPService } from '@/lib/mcp';

interface NetworkHeatmapProps {
  timeframe: string;
}

interface HeatmapData {
  labels: string[];
  datasets: {
    values: number[];
    colors: string[];
  };
}

export default function NetworkHeatmap({ timeframe }: NetworkHeatmapProps) {
  const [loading, setLoading] = useState<boolean>(true);
  const [data, setData] = useState<HeatmapData | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const mcpService = new MCPService();
        const response = await mcpService.get_channels_performance(timeframe);
        
        if (response && response.channels) {
          // Transformer les données pour la heatmap
          const channels = response.channels.slice(0, 20); // Limiter à 20 canaux pour la démo
          
          const labels = channels.map((channel: any) => 
            channel.alias ? channel.alias : `Canal ${channel.id.substring(0, 8)}`
          );
          
          const values = channels.map((channel: any) => channel.profit || 0);
          
          // Générer des couleurs basées sur la rentabilité
          const colors = values.map((value: number) => {
            if (value > 1000) return 'rgb(0, 200, 83)';
            if (value > 0) return 'rgb(0, 150, 136)';
            if (value > -500) return 'rgb(255, 152, 0)';
            return 'rgb(244, 67, 54)';
          });
          
          setData({
            labels,
            datasets: {
              values,
              colors
            }
          });
        }
      } catch (error) {
        console.error('Erreur lors de la récupération des données de performance:', error);
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

  if (!data) {
    return (
      <div className="text-center py-12 text-gray-400">
        Aucune donnée disponible pour la période sélectionnée
      </div>
    );
  }

  return (
    <div className="overflow-hidden">
      <div className="grid grid-cols-5 gap-2">
        {data.labels.map((label, index) => (
          <div key={index} className="text-center">
            <div 
              className="h-24 rounded-md flex items-center justify-center mb-2"
              style={{ backgroundColor: data.datasets.colors[index] }}
            >
              <span className="text-lg font-bold text-white">
                {data.datasets.values[index] > 0 ? '+' : ''}
                {data.datasets.values[index]}
              </span>
            </div>
            <p className="text-xs text-gray-300 truncate" title={label}>
              {label}
            </p>
          </div>
        ))}
      </div>

      <div className="flex justify-between mt-4">
        <div className="flex items-center gap-2">
          <span className="inline-block w-3 h-3 rounded-full bg-red-500"></span>
          <span className="text-xs text-gray-400">Très négatif</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-block w-3 h-3 rounded-full bg-orange-500"></span>
          <span className="text-xs text-gray-400">Légèrement négatif</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-block w-3 h-3 rounded-full bg-teal-600"></span>
          <span className="text-xs text-gray-400">Positif</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-block w-3 h-3 rounded-full bg-green-500"></span>
          <span className="text-xs text-gray-400">Très positif</span>
        </div>
      </div>
    </div>
  );
} 