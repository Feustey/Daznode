'use client';

import { useState, FormEvent } from 'react';
import NavBar from '@/components/layout/NavBar';
import { isAuthenticated, logout, authenticateLocal } from '@/lib/utils/AuthUtils';

interface SettingsState {
  password: string;
  isAuth: boolean;
  error: string | null;
  success: string | null;
  refreshInterval: number;
  enableLiveUpdates: boolean;
}

export default function SettingsPage() {
  const [state, setState] = useState<SettingsState>({
    password: '',
    isAuth: isAuthenticated(),
    error: null,
    success: null,
    refreshInterval: 60,
    enableLiveUpdates: true
  });

  const handleLogin = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setState(prev => ({ ...prev, error: null, success: null }));

    try {
      const result = await authenticateLocal(state.password);
      if (result) {
        setState(prev => ({
          ...prev,
          isAuth: true,
          success: 'Authentification réussie!',
          password: ''
        }));
      } else {
        setState(prev => ({
          ...prev,
          error: 'Mot de passe incorrect'
        }));
      }
    } catch (err) {
      setState(prev => ({
        ...prev,
        error: 'Erreur lors de l\'authentification'
      }));
      console.error(err);
    }
  };

  const handleLogout = () => {
    logout();
    setState(prev => ({
      ...prev,
      isAuth: false,
      success: 'Déconnexion réussie'
    }));
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setState(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  return (
    <main className="min-h-screen">
      <NavBar />
      <div className="container mx-auto p-6">
        <h1 className="text-2xl font-bold mb-6">Paramètres</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Section Authentification */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold mb-4">Authentification</h2>
            
            {state.isAuth ? (
              <div>
                <p className="mb-4 text-green-500">✓ Vous êtes authentifié</p>
                <button
                  onClick={handleLogout}
                  className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded transition-colors"
                >
                  Se déconnecter
                </button>
              </div>
            ) : (
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <label htmlFor="password" className="block mb-2 text-sm font-medium">
                    Mot de passe
                  </label>
                  <input
                    type="password"
                    id="password"
                    name="password"
                    value={state.password}
                    onChange={handleInputChange}
                    className="w-full p-2 bg-gray-800 border border-gray-700 rounded-md text-white"
                    required
                  />
                </div>
                
                <button
                  type="submit"
                  className="bg-accent-blue hover:bg-blue-600 text-white px-4 py-2 rounded transition-colors"
                >
                  Se connecter
                </button>
                
                {state.error && <p className="text-red-500 text-sm">{state.error}</p>}
                {state.success && <p className="text-green-500 text-sm">{state.success}</p>}
              </form>
            )}
          </div>
          
          {/* Section Interface */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold mb-4">Interface</h2>
            <div className="space-y-4">
              <div>
                <label htmlFor="refreshInterval" className="block mb-2 text-sm font-medium">
                  Intervalle de rafraîchissement (secondes)
                </label>
                <input
                  type="number"
                  id="refreshInterval"
                  name="refreshInterval"
                  value={state.refreshInterval}
                  onChange={handleInputChange}
                  min="10"
                  max="600"
                  className="w-full p-2 bg-gray-800 border border-gray-700 rounded-md text-white"
                />
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="enableLiveUpdates"
                  name="enableLiveUpdates"
                  checked={state.enableLiveUpdates}
                  onChange={handleInputChange}
                  className="mr-2"
                />
                <label htmlFor="enableLiveUpdates" className="text-sm font-medium">
                  Activer les mises à jour en temps réel
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
} 