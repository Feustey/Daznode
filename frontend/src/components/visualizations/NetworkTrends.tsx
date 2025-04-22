'use client';

import { useEffect, useRef, useState } from 'react';
import { Chart, registerables } from 'chart.js';
import { MCPService } from '@/lib/mcp';

// Enregistrer les composants Chart.js nécessaires
Chart.register(...registerables);

interface NetworkTrendsProps {
  timeframe: string;
}

interface TrendData {
  labels: string[];
  nodes: number[];
  channels: number[];
  capacity: number[];
}

export default function NetworkTrends({ timeframe }: NetworkTrendsProps) {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [data, setData] = useState<TrendData | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const mcpService = new MCPService();
        const response = await mcpService.get_network_growth_trends();
        
        if (response && response.trends) {
          const trends = response.trends;
          
          // Filtrer selon la période sélectionnée
          let filteredTrends = trends;
          if (timeframe === 'week') {
            filteredTrends = trends.slice(-7); // 7 derniers jours
          } else if (timeframe === 'month') {
            filteredTrends = trends.slice(-30); // 30 derniers jours
          } else if (timeframe === 'quarter') {
            filteredTrends = trends.slice(-90); // 90 derniers jours
          }
          
          // Formater les données pour le graphique
          const formattedData = {
            labels: filteredTrends.map((item: any) => item.date),
            nodes: filteredTrends.map((item: any) => item.num_nodes),
            channels: filteredTrends.map((item: any) => item.num_channels),
            capacity: filteredTrends.map((item: any) => item.total_capacity / 100000000), // BTC
          };
          
          setData(formattedData);
        }
      } catch (error) {
        console.error('Erreur lors de la récupération des tendances:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [timeframe]);

  useEffect(() => {
    if (!data || !chartRef.current) return;
    
    // Détruire le graphique précédent s'il existe
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }
    
    const ctx = chartRef.current.getContext('2d');
    if (!ctx) return;
    
    // Créer un nouveau graphique
    chartInstance.current = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.labels,
        datasets: [
          {
            label: 'Nœuds (x1000)',
            data: data.nodes.map(value => value / 1000),
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.1)',
            tension: 0.4,
            fill: true,
          },
          {
            label: 'Canaux (x1000)',
            data: data.channels.map(value => value / 1000),
            borderColor: 'rgb(153, 102, 255)',
            backgroundColor: 'rgba(153, 102, 255, 0.1)',
            tension: 0.4,
            fill: true,
          },
          {
            label: 'Capacité (BTC)',
            data: data.capacity,
            borderColor: 'rgb(255, 159, 64)',
            backgroundColor: 'rgba(255, 159, 64, 0.1)',
            tension: 0.4,
            fill: true,
            yAxisID: 'y1',
          }
        ]
      },
      options: {
        responsive: true,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        scales: {
          x: {
            grid: {
              color: 'rgba(255, 255, 255, 0.1)',
            },
            ticks: {
              color: 'rgba(255, 255, 255, 0.7)',
            }
          },
          y: {
            grid: {
              color: 'rgba(255, 255, 255, 0.1)',
            },
            ticks: {
              color: 'rgba(255, 255, 255, 0.7)',
            }
          },
          y1: {
            position: 'right',
            grid: {
              display: false,
            },
            ticks: {
              color: 'rgba(255, 159, 64, 0.7)',
            }
          }
        },
        plugins: {
          legend: {
            position: 'top',
            labels: {
              color: 'rgba(255, 255, 255, 0.7)',
            }
          },
          tooltip: {
            mode: 'index',
          }
        }
      }
    });
    
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [data]);

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
        Aucune donnée de tendance disponible
      </div>
    );
  }

  return (
    <div className="h-96">
      <canvas ref={chartRef} />
    </div>
  );
} 