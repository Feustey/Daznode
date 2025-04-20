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

/**
 * Formater un montant en sats avec unité
 * @param value - Montant en sats
 */
export function formatSats(value: number): string {
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(2)}M sats`;
  } else if (value >= 1000) {
    return `${(value / 1000).toFixed(2)}K sats`;
  }
  return `${value} sats`;
}

/**
 * Formatage d'une durée pour l'affichage
 * @param durationString - Chaîne de durée au format "XXd XXh XXm"
 */
export function formatDuration(durationString: string): string {
  return durationString;
}

/**
 * Obtenir une classe CSS de couleur selon la variation
 * @param percentChange - Pourcentage de variation
 */
export function getChangeColorClass(percentChange: number): string {
  if (percentChange > 0) return 'text-green-500';
  if (percentChange < 0) return 'text-red-500';
  return 'text-gray-400';
}

/**
 * Formater une date relative (il y a X temps)
 * @param dateString - Chaîne de date
 */
export function formatRelativeTime(dateString: string): string {
  return dateString;
} 