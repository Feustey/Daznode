'use client';

import { useState, useRef, ReactNode } from 'react';

interface TooltipProps {
  content: ReactNode;
  children: ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
}

export default function Tooltip({
  content,
  children,
  position = 'top',
  className = '',
}: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Déterminer la position du tooltip
  const getPositionClasses = () => {
    switch (position) {
      case 'bottom':
        return 'top-full mt-2';
      case 'left':
        return 'right-full mr-2';
      case 'right':
        return 'left-full ml-2';
      case 'top':
      default:
        return 'bottom-full mb-2';
    }
  };

  const handleMouseEnter = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsVisible(true);
  };

  const handleMouseLeave = () => {
    timeoutRef.current = setTimeout(() => {
      setIsVisible(false);
    }, 200);
  };

  return (
    <div
      className="relative inline-block"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onFocus={handleMouseEnter}
      onBlur={handleMouseLeave}
      tabIndex={0}
    >
      {children}
      
      {isVisible && (
        <div
          className={`absolute z-50 px-3 py-2 text-sm rounded shadow-lg bg-gray-800 text-white whitespace-nowrap max-w-xs ${getPositionClasses()} ${className}`}
          style={{ transform: 'translateX(-50%)', left: '50%' }}
        >
          {content}
          <div
            className={`absolute w-2 h-2 bg-gray-800 transform rotate-45 ${
              position === 'bottom' ? 'top-0 -translate-y-1/2' :
              position === 'top' ? 'bottom-0 translate-y-1/2' :
              position === 'left' ? 'right-0 translate-x-1/2' :
              'left-0 -translate-x-1/2'
            }`}
            style={{ 
              left: position === 'top' || position === 'bottom' ? '50%' : 'auto',
              top: position === 'left' || position === 'right' ? '50%' : 'auto'
            }}
          />
        </div>
      )}
    </div>
  );
} 