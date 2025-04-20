export interface NodeData {
  alias: string;
  pubkey: string;
  customTags?: string[];
  isFavorite?: boolean;
  stats: {
    capacity: {
      total: number;
      percentChange: number;
    };
    channels: {
      count: number;
      percentChange: number;
      biggest: number;
      smallest: number;
      average: number;
      median: number;
    };
    timeData: {
      lastUpdate: string;
      aot: string;
      oldest: string;
      youngest: string;
      averageAge: string;
      medianAge: string;
    };
    rankings: {
      channels: {
        rank: number;
        change: number;
      };
      capacity: {
        rank: number;
        change: number;
      };
    };
  };
  identifiers: {
    torAddress?: string;
    link?: string;
  };
  historicalData: {
    channels: {
      data: Array<{day: number; count: number}>;
    };
    capacity: {
      data: Array<{day: number; amount: number}>;
    };
  };
} 