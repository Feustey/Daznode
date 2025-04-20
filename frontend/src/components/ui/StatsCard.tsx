import { ReactNode } from 'react';
import Tooltip from './Tooltip';
import { getChangeColorClass } from '@/lib/utils/formatters';
import { InformationCircleIcon } from '@heroicons/react/24/outline';

interface StatsCardProps {
  label: string;
  value: string | number;
  subValue?: string;
  percentChange?: number;
  tooltip?: ReactNode;
}

export default function StatsCard({ 
  label, 
  value, 
  subValue, 
  percentChange,
  tooltip
}: StatsCardProps) {
  return (
    <div className="card flex flex-col p-4">
      <div className="flex items-center">
        <span className="stat-label">{label}</span>
        {tooltip && (
          <Tooltip content={tooltip} position="top">
            <span className="ml-1 cursor-help">
              <InformationCircleIcon className="h-4 w-4 text-gray-400" />
            </span>
          </Tooltip>
        )}
      </div>
      
      <div className="flex items-baseline">
        <span className="stat-value">{value}</span>
        {subValue && (
          <span className="text-xs text-gray-400 ml-1">{subValue}</span>
        )}
      </div>
      
      {percentChange !== undefined && (
        <div className={`text-xs mt-1 ${getChangeColorClass(percentChange)}`}>
          {percentChange > 0 && '+'}{percentChange}%
        </div>
      )}
    </div>
  );
} 