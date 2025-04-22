'use client';

import { useState } from 'react';
import NavBar from '@/components/layout/NavBar';
import NetworkHeatmap from '@/components/visualizations/NetworkHeatmap';
import NetworkGraph from '@/components/visualizations/NetworkGraph';
import NetworkTrends from '@/components/visualizations/NetworkTrends';
import ChannelProfitability from '@/components/visualizations/ChannelProfitability';
import NodeComparison from '@/components/visualizations/NodeComparison';

export default function Overview() {
  const [selectedTimeframe, setSelectedTimeframe] = useState<string>('week');

  const timeframes = [
    { value: 'day', label: 'Jour' },
    { value: 'week', label: 'Semaine' },
    { value: 'month', label: 'Mois' },
    { value: 'quarter', label: 'Trimestre' },
    { value: 'year', label: 'Année' },
  ];

  return (
    <main className="min-h-screen bg-gray-950">
      <NavBar />
      
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6 text-white">Vue d'ensemble du réseau</h1>
        
        <div className="mb-6 flex justify-end">
          <div className="inline-flex bg-gray-800 rounded-md">
            {timeframes.map((timeframe) => (
              <button
                key={timeframe.value}
                className={`px-4 py-2 text-sm font-medium ${
                  selectedTimeframe === timeframe.value
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700'
                } rounded-md`}
                onClick={() => setSelectedTimeframe(timeframe.value)}
              >
                {timeframe.label}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-gray-900 rounded-lg p-6 shadow-xl">
            <h2 className="text-xl font-bold mb-4 text-white">Carte de chaleur des canaux</h2>
            <NetworkHeatmap timeframe={selectedTimeframe} />
          </div>
          
          <div className="bg-gray-900 rounded-lg p-6 shadow-xl">
            <h2 className="text-xl font-bold mb-4 text-white">Graphe du réseau</h2>
            <NetworkGraph />
          </div>
        </div>

        <div className="bg-gray-900 rounded-lg p-6 shadow-xl mb-8">
          <h2 className="text-xl font-bold mb-4 text-white">Tendances du réseau</h2>
          <NetworkTrends timeframe={selectedTimeframe} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-gray-900 rounded-lg p-6 shadow-xl">
            <h2 className="text-xl font-bold mb-4 text-white">Matrice de rentabilité des canaux</h2>
            <ChannelProfitability timeframe={selectedTimeframe} />
          </div>
          
          <div className="bg-gray-900 rounded-lg p-6 shadow-xl">
            <h2 className="text-xl font-bold mb-4 text-white">Comparaison de nœuds</h2>
            <NodeComparison />
          </div>
        </div>
      </div>
    </main>
  );
} 