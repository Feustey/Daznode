import { NodeData } from '@/lib/types/node';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface HistoricalChartsProps {
  nodeData: NodeData;
}

export default function HistoricalCharts({ nodeData }: HistoricalChartsProps) {
  // Vérifier si les données historiques existent
  const historicalData = nodeData?.historicalData || {
    channels: { data: [] },
    capacity: { data: [] }
  };

  // Si aucune donnée n'est disponible, afficher un message
  if (!historicalData.channels.data?.length || !historicalData.capacity.data?.length) {
    return (
      <div className="grid grid-cols-1 gap-6">
        <div className="card p-4">
          <h3 className="text-xl font-medium">Données historiques</h3>
          <p className="text-gray-400 mt-2">Aucune donnée historique disponible pour ce nœud</p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Graphique des canaux */}
      <div className="card p-4">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-xl font-medium">Channels</h3>
          <button className="text-pink-400 hover:text-pink-300 text-sm">
            View Historicals
          </button>
        </div>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={historicalData.channels.data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis 
                dataKey="day" 
                stroke="#666" 
                tick={{ fill: '#999' }} 
              />
              <YAxis 
                stroke="#666" 
                tick={{ fill: '#999' }} 
                domain={['auto', 'auto']}
              />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1F1F28', border: 'none', color: '#fff' }} 
                labelStyle={{ color: '#fff' }}
              />
              <Line 
                type="monotone" 
                dataKey="count" 
                stroke="#3B82F6" 
                strokeWidth={2} 
                dot={{ r: 3, fill: '#3B82F6' }} 
                activeDot={{ r: 5 }} 
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Graphique de la capacité */}
      <div className="card p-4">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-xl font-medium">Capacity</h3>
          <button className="text-pink-400 hover:text-pink-300 text-sm">
            View Historicals
          </button>
        </div>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={historicalData.capacity.data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis 
                dataKey="day" 
                stroke="#666" 
                tick={{ fill: '#999' }} 
              />
              <YAxis 
                stroke="#666" 
                tick={{ fill: '#999' }} 
                domain={['auto', 'auto']}
                tickFormatter={(value) => `${(value/1000000).toFixed(1)}m`}
              />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1F1F28', border: 'none', color: '#fff' }} 
                labelStyle={{ color: '#fff' }}
                formatter={(value: number) => [`${value.toLocaleString()} sats`, 'Amount']}
              />
              <Line 
                type="monotone" 
                dataKey="amount" 
                stroke="#EF4444" 
                strokeWidth={2} 
                dot={{ r: 3, fill: '#EF4444' }} 
                activeDot={{ r: 5 }} 
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
} 