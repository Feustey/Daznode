/**
 * Fonctions utilitaires pour la gestion de l'authentification
 */

interface User {
  username: string;
  role: string;
  [key: string]: unknown;
}

// Configuration de base
const AUTH_TOKEN_KEY = 'daznode_auth_token';
const AUTH_USER_KEY = 'daznode_user';

/**
 * Stocke un token d'authentification dans le stockage local
 * @param token - Token JWT à stocker
 */
export function setAuthToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
  }
}

/**
 * Récupère le token d'authentification du stockage local
 * @returns Le token JWT ou null s'il n'existe pas
 */
export function getAuthToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(AUTH_TOKEN_KEY);
  }
  return null;
}

/**
 * Supprime le token d'authentification du stockage local
 */
export function removeAuthToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(AUTH_TOKEN_KEY);
  }
}

/**
 * Vérifie si l'utilisateur est authentifié
 * @returns Vrai si un token est présent, faux sinon
 */
export function isAuthenticated(): boolean {
  return !!getAuthToken();
}

/**
 * Stocke les informations utilisateur dans le stockage local
 * @param user - Objet utilisateur à stocker
 */
export function setUser(user: User): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
  }
}

/**
 * Récupère les informations utilisateur du stockage local
 * @returns L'objet utilisateur ou null s'il n'existe pas
 */
export function getUser(): User | null {
  if (typeof window !== 'undefined') {
    const userStr = localStorage.getItem(AUTH_USER_KEY);
    if (userStr) {
      try {
        return JSON.parse(userStr) as User;
      } catch (e) {
        console.error("Erreur lors de l'analyse des données utilisateur:", e);
      }
    }
  }
  return null;
}

/**
 * Supprime les informations utilisateur du stockage local
 */
export function removeUser(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(AUTH_USER_KEY);
  }
}

/**
 * Déconnecte l'utilisateur en supprimant toutes les données d'authentification
 */
export function logout(): void {
  removeAuthToken();
  removeUser();
}

/**
 * Authentification simple avec mot de passe local (pour l'environnement Umbrel)
 * @param password - Mot de passe à vérifier
 * @returns Promesse résolue avec un booléen indiquant si l'authentification a réussi
 */
export async function authenticateLocal(password: string): Promise<boolean> {
  // Dans un environnement Umbrel, on pourrait utiliser un mot de passe simple stocké localement
  // ou via une API d'authentification locale
  
  // Pour le développement, acceptons un mot de passe simple
  const devPassword = process.env.NEXT_PUBLIC_DEV_PASSWORD || 'umbrel';
  
  if (password === devPassword) {
    // Créer un token factice pour le développement
    const mockToken = `dev_token_${Date.now()}`;
    setAuthToken(mockToken);
    setUser({ username: 'admin', role: 'admin' });
    return true;
  }
  
  return false;
} 