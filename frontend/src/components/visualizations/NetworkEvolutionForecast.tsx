'use client';

import { useEffect, useRef, useState } from 'react';
import { Chart, registerables } from 'chart.js';
import { MCPService } from '@/lib/mcp';

// Enregistrer les composants Chart.js nécessaires
Chart.register(...registerables);

interface NetworkEvolutionForecastProps {
  timeframe: string;
}

interface TrendPoint {
  date: string;
  value: number;
}

interface ForecastData {
  historicalDates: string[];
  historicalNodes: number[];
  historicalChannels: number[];
  historicalCapacity: number[];
  forecastDates: string[];
  forecastNodes: number[];
  forecastChannels: number[];
  forecastCapacity: number[];
}

export default function NetworkEvolutionForecast({ timeframe }: NetworkEvolutionForecastProps) {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [data, setData] = useState<ForecastData | null>(null);
  const [selectedMetric, setSelectedMetric] = useState<string>('nodes');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const mcpService = new MCPService();
        const response = await mcpService.get_network_growth_trends();
        
        if (response && response.trends) {
          // Récupérer l'historique
          const trends = response.trends;
          
          // Filtrer selon la période sélectionnée
          let historicalData = [...trends];
          if (timeframe === 'month') {
            historicalData = trends.slice(-30); // 30 derniers jours
          } else if (timeframe === 'quarter') {
            historicalData = trends.slice(-90); // 90 derniers jours
          } else if (timeframe === 'year') {
            historicalData = trends.slice(-365); // 365 derniers jours
          }
          
          // Générer des prévisions basées sur les tendances actuelles
          // Note: Dans une application réelle, cela utiliserait des algorithmes de prédiction plus sophistiqués
          const generateForecast = (data: TrendPoint[]): TrendPoint[] => {
            if (data.length < 2) return [];
            
            // Calculer le taux de croissance moyen
            const values = data.map(point => point.value);
            const growthRates = [];
            
            for (let i = 1; i < values.length; i++) {
              const rate = (values[i] - values[i-1]) / values[i-1];
              growthRates.push(rate);
            }
            
            // Taux de croissance moyen
            const avgGrowthRate = growthRates.reduce((a, b) => a + b, 0) / growthRates.length;
            
            // Générer 10 points de données futurs
            const lastValue = values[values.length - 1];
            const lastDate = new Date(data[data.length - 1].date);
            
            const forecast: TrendPoint[] = [];
            
            for (let i = 1; i <= 10; i++) {
              const nextDate = new Date(lastDate);
              nextDate.setDate(lastDate.getDate() + i);
              
              // Calculer la nouvelle valeur avec le taux de croissance
              const nextValue = lastValue * Math.pow(1 + avgGrowthRate, i);
              
              forecast.push({
                date: nextDate.toISOString().split('T')[0],
                value: Math.round(nextValue)
              });
            }
            
            return forecast;
          };
          
          // Préparer l'historique des données
          const nodeHistory: TrendPoint[] = historicalData.map(item => ({
            date: item.date,
            value: item.num_nodes
          }));
          
          const channelHistory: TrendPoint[] = historicalData.map(item => ({
            date: item.date,
            value: item.num_channels
          }));
          
          const capacityHistory: TrendPoint[] = historicalData.map(item => ({
            date: item.date,
            value: Math.round(item.total_capacity / 100000000) // en BTC
          }));
          
          // Générer les prévisions
          const nodeForecast = generateForecast(nodeHistory);
          const channelForecast = generateForecast(channelHistory);
          const capacityForecast = generateForecast(capacityHistory);
          
          // Formater les données pour le graphique
          setData({
            historicalDates: nodeHistory.map(item => item.date),
            historicalNodes: nodeHistory.map(item => item.value),
            historicalChannels: channelHistory.map(item => item.value),
            historicalCapacity: capacityHistory.map(item => item.value),
            forecastDates: nodeForecast.map(item => item.date),
            forecastNodes: nodeForecast.map(item => item.value),
            forecastChannels: channelForecast.map(item => item.value),
            forecastCapacity: capacityForecast.map(item => item.value)
          });
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
    
    // Données à afficher selon la métrique sélectionnée
    let historicalValues: number[] = [];
    let forecastValues: number[] = [];
    let label = '';
    
    switch (selectedMetric) {
      case 'nodes':
        historicalValues = data.historicalNodes;
        forecastValues = data.forecastNodes;
        label = 'Nombre de nœuds';
        break;
      case 'channels':
        historicalValues = data.historicalChannels;
        forecastValues = data.forecastChannels;
        label = 'Nombre de canaux';
        break;
      case 'capacity':
        historicalValues = data.historicalCapacity;
        forecastValues = data.forecastCapacity;
        label = 'Capacité totale (BTC)';
        break;
    }
    
    // Créer un nouveau graphique
    chartInstance.current = new Chart(ctx, {
      type: 'line',
      data: {
        labels: [...data.historicalDates, ...data.forecastDates],
        datasets: [
          {
            label: 'Historique',
            data: [...historicalValues, ...Array(data.forecastDates.length).fill(null)],
            borderColor: 'rgb(53, 162, 235)',
            backgroundColor: 'rgba(53, 162, 235, 0.5)',
            tension: 0.4,
            pointRadius: 3,
          },
          {
            label: 'Prévisions',
            data: [...Array(data.historicalDates.length).fill(null), ...forecastValues],
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            borderDash: [5, 5],
            tension: 0.4,
            pointRadius: 3,
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              color: 'rgba(255, 255, 255, 0.7)',
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false,
          },
          title: {
            display: true,
            text: `Évolution et prévisions - ${label}`,
            color: 'rgba(255, 255, 255, 0.9)',
            font: {
              size: 16
            }
          }
        },
        scales: {
          x: {
            grid: {
              color: 'rgba(255, 255, 255, 0.1)',
            },
            ticks: {
              color: 'rgba(255, 255, 255, 0.7)',
              maxRotation: 45,
              minRotation: 45
            }
          },
          y: {
            grid: {
              color: 'rgba(255, 255, 255, 0.1)',
            },
            ticks: {
              color: 'rgba(255, 255, 255, 0.7)',
            }
          }
        }
      }
    });
  }, [data, selectedMetric]);

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
        Impossible de charger les données de tendance
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-center space-x-4 mb-4">
        <button
          onClick={() => setSelectedMetric('nodes')}
          className={`px-4 py-2 rounded ${
            selectedMetric === 'nodes'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          Nœuds
        </button>
        <button
          onClick={() => setSelectedMetric('channels')}
          className={`px-4 py-2 rounded ${
            selectedMetric === 'channels'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          Canaux
        </button>
        <button
          onClick={() => setSelectedMetric('capacity')}
          className={`px-4 py-2 rounded ${
            selectedMetric === 'capacity'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          Capacité
        </button>
      </div>
      
      <div className="h-96">
        <canvas ref={chartRef} />
      </div>
      
      <div className="bg-blue-900 bg-opacity-20 p-4 rounded-md border border-blue-700">
        <h4 className="text-blue-400 font-medium mb-2">À propos des prévisions</h4>
        <p className="text-sm text-gray-300">
          Ces prévisions sont basées sur l'analyse des tendances historiques et utilisent un modèle de croissance exponentielle. 
          Elles sont purement indicatives et ne tiennent pas compte des événements futurs qui pourraient influencer l'évolution 
          du réseau Lightning. 
        </p>
      </div>
    </div>
  );
} 