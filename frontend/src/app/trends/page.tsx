'use client';

import { useState } from 'react';
import NavBar from '@/components/layout/NavBar';
import UnprofitableChannelsWithSuggestions from '@/components/visualizations/UnprofitableChannelsWithSuggestions';
import NetworkEvolutionForecast from '@/components/visualizations/NetworkEvolutionForecast';
import PotentialPeersRanking from '@/components/visualizations/PotentialPeersRanking';

export default function Trends() {
  const [selectedTimeframe, setSelectedTimeframe] = useState<string>('month');

  const timeframes = [
    { value: 'week', label: 'Semaine' },
    { value: 'month', label: 'Mois' },
    { value: 'quarter', label: 'Trimestre' },
    { value: 'year', label: 'Année' },
  ];

  return (
    <main className="min-h-screen bg-gray-950">
      <NavBar />
      
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6 text-white">Tendances & Prévisions</h1>
        
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

        <div className="grid grid-cols-1 gap-8 mb-8">
          <div className="bg-gray-900 rounded-lg p-6 shadow-xl">
            <h2 className="text-xl font-bold mb-4 text-white">Canaux non rentables avec suggestions</h2>
            <UnprofitableChannelsWithSuggestions timeframe={selectedTimeframe} />
          </div>
        </div>

        <div className="bg-gray-900 rounded-lg p-6 shadow-xl mb-8">
          <h2 className="text-xl font-bold mb-4 text-white">Évolution du réseau avec prévisions</h2>
          <NetworkEvolutionForecast timeframe={selectedTimeframe} />
        </div>

        <div className="bg-gray-900 rounded-lg p-6 shadow-xl">
          <h2 className="text-xl font-bold mb-4 text-white">Classement des nœuds pairs potentiels</h2>
          <PotentialPeersRanking />
        </div>
      </div>
    </main>
  );
} 