'use client';

import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';

interface LiveIndicatorProps {
  lastUpdate: Date | null;
  isLive: boolean;
  className?: string;
}

export default function LiveIndicator({ lastUpdate, isLive, className = '' }: LiveIndicatorProps) {
  const [timeAgo, setTimeAgo] = useState<string>('');
  const [pulseColor, setPulseColor] = useState<string>('bg-green-500');

  // Mettre à jour le temps écoulé depuis la dernière mise à jour
  useEffect(() => {
    if (!lastUpdate) {
      setTimeAgo('Jamais');
      setPulseColor('bg-gray-500');
      return;
    }

    const updateTimeAgo = () => {
      const now = new Date();
      const diff = now.getTime() - lastUpdate.getTime();
      
      // Convertir la différence en une chaîne lisible
      if (diff < 10000) { // moins de 10 secondes
        setTimeAgo('à l\'instant');
        setPulseColor('bg-green-500');
      } else if (diff < 60000) { // moins d'une minute
        setTimeAgo(`il y a ${Math.floor(diff / 1000)}s`);
        setPulseColor('bg-green-500');
      } else if (diff < 300000) { // moins de 5 minutes
        setTimeAgo(`il y a ${Math.floor(diff / 60000)}m`);
        setPulseColor('bg-green-500');
      } else if (diff < 3600000) { // moins d'une heure
        setTimeAgo(`il y a ${Math.floor(diff / 60000)}m`);
        setPulseColor('bg-yellow-500');
      } else {
        setTimeAgo(`il y a ${Math.floor(diff / 3600000)}h`);
        setPulseColor('bg-red-500');
      }
    };

    // Exécuter immédiatement
    updateTimeAgo();
    
    // Puis mettre à jour toutes les secondes
    const intervalId = setInterval(updateTimeAgo, 1000);
    
    return () => clearInterval(intervalId);
  }, [lastUpdate]);

  return (
    <div className={cn('flex items-center', className)}>
      {isLive ? (
        <div className="flex items-center">
          <span className="relative flex h-3 w-3 mr-2">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${pulseColor} opacity-75`}></span>
            <span className={`relative inline-flex rounded-full h-3 w-3 ${pulseColor}`}></span>
          </span>
          <span className="text-xs">LIVE</span>
        </div>
      ) : (
        <div className="flex items-center">
          <span className="relative flex h-3 w-3 mr-2">
            <span className="relative inline-flex rounded-full h-3 w-3 bg-gray-500"></span>
          </span>
          <span className="text-xs">HORS LIGNE</span>
        </div>
      )}
      
      <span className="ml-2 text-xs text-gray-400">
        Dernière mise à jour: {timeAgo}
      </span>
    </div>
  );
} 