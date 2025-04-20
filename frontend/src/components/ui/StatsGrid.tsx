import { NodeData } from '@/lib/types/node';
import StatsCard from './StatsCard';
import { formatNumber } from '@/lib/hooks/useNodeData';

interface StatsGridProps {
  nodeData: NodeData;
}

export default function StatsGrid({ nodeData }: StatsGridProps) {
  const { stats } = nodeData;
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-6">
      {/* Colonne gauche */}
      <div className="flex flex-col gap-4">
        <StatsCard 
          label="Total Capacity" 
          value={formatNumber(stats.capacity.total)} 
          subValue="sats" 
          percentChange={stats.capacity.percentChange} 
        />
        <StatsCard 
          label="Number of Channels" 
          value={stats.channels.count} 
          subValue="Channels" 
          percentChange={stats.channels.percentChange} 
        />
        <StatsCard 
          label="Last Update" 
          value={stats.timeData.lastUpdate} 
        />
        <StatsCard 
          label="AOT" 
          value={stats.timeData.aot} 
        />
      </div>
      
      {/* Colonne centrale */}
      <div className="flex flex-col gap-4">
        <StatsCard 
          label="Biggest Channel" 
          value={formatNumber(stats.channels.biggest)} 
          subValue="sats" 
        />
        <StatsCard 
          label="Smallest Channel" 
          value={formatNumber(stats.channels.smallest)} 
          subValue="sats" 
        />
        <StatsCard 
          label="Average Size Channel" 
          value={formatNumber(stats.channels.average)} 
          subValue="sats" 
        />
        <StatsCard 
          label="Median Size Channel" 
          value={formatNumber(stats.channels.median)} 
          subValue="sats" 
        />
      </div>
      
      {/* Colonne droite */}
      <div className="flex flex-col gap-4">
        <StatsCard 
          label="Oldest Channel" 
          value={stats.timeData.oldest} 
        />
        <StatsCard 
          label="Youngest Channel" 
          value={stats.timeData.youngest} 
        />
        <StatsCard 
          label="Average Age Channel" 
          value={stats.timeData.averageAge} 
        />
        <StatsCard 
          label="Median Age Channel" 
          value={stats.timeData.medianAge} 
        />
      </div>
    </div>
  );
} 