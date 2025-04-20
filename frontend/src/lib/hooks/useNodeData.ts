import useSWR from 'swr';
import { getNodeData } from '../api/nodeApi';
import { NodeData } from '../types/node';

// Le pubkey de Feustey pour le développement
const FEUSTEY_PUBKEY = '02778f4a4eb3a2344b9fd8ee72e7ec5f03f803e5f5273e2e1a2af508910cf2b12b';

/**
 * Hook personnalisé pour récupérer les données d'un nœud Lightning
 * @param pubkey - Clé publique du nœud Lightning (optionnelle, par défaut Feustey)
 * @param refreshInterval - Intervalle de rafraîchissement en ms (optionnel, par défaut 60000ms = 1min)
 */
export function useNodeData(pubkey: string = FEUSTEY_PUBKEY, refreshInterval: number = 60000) {
  const { data, error, isLoading, mutate } = useSWR<NodeData>(
    `node/${pubkey}`,
    () => getNodeData(pubkey),
    {
      refreshInterval,
      revalidateOnFocus: true,
      dedupingInterval: 5000,
    }
  );

  return {
    node: data,
    isLoading,
    isError: error,
    mutate,
  };
}

/**
 * Formatage d'un nombre avec séparateurs de milliers
 * @param value - Valeur à formater
 */
export function formatNumber(value: number): string {
  return new Intl.NumberFormat('fr-FR').format(value);
}

/**
 * Formater un pubkey pour l'affichage (version courte)
 * @param pubkey - Clé publique complète
 */
export function formatPubkey(pubkey: string): string {
  if (!pubkey || pubkey.length < 10) return pubkey;
  return `${pubkey.substring(0, 6)}...${pubkey.substring(pubkey.length - 6)}`;
} 