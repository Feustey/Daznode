import axios, { AxiosError } from 'axios';
import { NodeData } from '../types/node';

// Définir l'URL de base de l'API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// En mode développement, utiliser toujours les données mockées
const USE_MOCK_DATA = true; // process.env.NODE_ENV === 'development';

// Créer une instance axios avec configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

interface ApiError {
  message: string;
  status?: number;
}

// Récupérer les données d'un nœud par pubkey
export async function getNodeData(pubkey: string): Promise<NodeData> {
  // En mode développement, retourner directement les données mockées
  if (USE_MOCK_DATA) {
    console.log('Utilisation des données mockées pour le développement');
    return getMockNodeData(pubkey);
  }

  try {
    const response = await apiClient.get<NodeData>(`/node/${pubkey}`);
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError;
    console.error('Erreur lors de la récupération des données du nœud:', axiosError.message);
    
    // En cas d'erreur, retourner des données mockées
    return getMockNodeData(pubkey);
  }
}

// Fonction de données mockées pour le développement
export function getMockNodeData(pubkey: string): NodeData {
  return {
    alias: "Feustey",
    pubkey: pubkey,
    customTags: ["#GSpotSuperNode"],
    isFavorite: true,
    stats: {
      capacity: {
        total: 17965032,
        percentChange: 0,
      },
      channels: {
        count: 12,
        percentChange: 0,
        biggest: 3000000,
        smallest: 500000,
        average: 1497086,
        median: 1043613,
      },
      timeData: {
        lastUpdate: "1 hour ago",
        aot: "1h 29m",
        oldest: "57d 13h 20m",
        youngest: "7d 20h 40m",
        averageAge: "36d 18h 53m",
        medianAge: "42d 10m",
      },
      rankings: {
        channels: {
          rank: 1148,
          change: 3,
        },
        capacity: {
          rank: 1860,
          change: 1,
        },
      },
    },
    identifiers: {
      torAddress: "02778f4a4eb3a2344b9fd8ee72e7ec5f03f803e5f5273e2e1a2af508",
      link: "https://amboss.space/node/02778f4a4eb3a2344b9fd8ee72e7ec5f03f803e5f5273e2e1a2af508910cf2b12b",
    },
    historicalData: {
      channels: {
        data: [
          { day: 1, count: 18 },
          { day: 2, count: 17 },
          { day: 3, count: 16 },
          { day: 4, count: 15 },
          { day: 5, count: 15 },
          { day: 6, count: 15 },
          { day: 7, count: 15 },
          { day: 8, count: 15 },
          { day: 9, count: 15 },
          { day: 10, count: 16 },
          { day: 11, count: 15 },
          { day: 12, count: 12 },
          { day: 13, count: 12 },
          { day: 14, count: 12 },
          { day: 15, count: 12 },
          { day: 16, count: 12 },
          { day: 17, count: 12 },
          { day: 18, count: 12 },
          { day: 19, count: 12 },
        ]
      },
      capacity: {
        data: [
          { day: 1, amount: 21000000 },
          { day: 2, amount: 20500000 },
          { day: 3, amount: 20000000 },
          { day: 4, amount: 19000000 },
          { day: 5, amount: 18500000 },
          { day: 6, amount: 18500000 },
          { day: 7, amount: 18500000 },
          { day: 8, amount: 18500000 },
          { day: 9, amount: 18500000 },
          { day: 10, amount: 19500000 },
          { day: 11, amount: 18500000 },
          { day: 12, amount: 17900000 },
          { day: 13, amount: 17900000 },
          { day: 14, amount: 17900000 },
          { day: 15, amount: 17900000 },
          { day: 16, amount: 17900000 },
          { day: 17, amount: 17900000 },
          { day: 18, amount: 17900000 },
          { day: 19, amount: 17965032 },
        ]
      }
    }
  };
} 