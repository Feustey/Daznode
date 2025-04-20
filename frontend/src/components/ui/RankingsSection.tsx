import { NodeData } from '@/lib/types/node';
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/solid';

interface RankingsSectionProps {
  nodeData: NodeData;
}

export default function RankingsSection({ nodeData }: RankingsSectionProps) {
  const { rankings } = nodeData.stats;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <div className="card p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-medium">Channels Rank:</h3>
          <div className="flex items-center">
            <span className="text-2xl font-bold">{rankings.channels.rank}</span>
            {rankings.channels.change !== 0 && (
              <div className="flex items-center ml-2">
                {rankings.channels.change > 0 ? (
                  <ArrowUpIcon className="h-5 w-5 text-green-500" />
                ) : (
                  <ArrowDownIcon className="h-5 w-5 text-red-500" />
                )}
                <span className={rankings.channels.change > 0 ? 'text-green-500' : 'text-red-500'}>
                  {Math.abs(rankings.channels.change)}
                </span>
              </div>
            )}
          </div>
        </div>
        <button className="text-pink-400 hover:text-pink-300 text-sm">
          View Historicals
        </button>
      </div>

      <div className="card p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-medium">Capacity Rank:</h3>
          <div className="flex items-center">
            <span className="text-2xl font-bold">{rankings.capacity.rank}</span>
            {rankings.capacity.change !== 0 && (
              <div className="flex items-center ml-2">
                {rankings.capacity.change > 0 ? (
                  <ArrowUpIcon className="h-5 w-5 text-green-500" />
                ) : (
                  <ArrowDownIcon className="h-5 w-5 text-red-500" />
                )}
                <span className={rankings.capacity.change > 0 ? 'text-green-500' : 'text-red-500'}>
                  {Math.abs(rankings.capacity.change)}
                </span>
              </div>
            )}
          </div>
        </div>
        <button className="text-pink-400 hover:text-pink-300 text-sm">
          View Historicals
        </button>
      </div>
    </div>
  );
} 