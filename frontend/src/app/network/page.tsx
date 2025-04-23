'use client';

import { useState } from 'react';
import { BarChart3, Search, Zap } from 'lucide-react';

export default function NetworkPage() {
  const [isLoading] = useState(true);

  return (
    <>
      {/* Hero Section */}
      <section className="section min-h-[40vh] flex flex-col items-center justify-center text-center">
        <h1 className="hero-title mb-6">
          Réseau Lightning
        </h1>
        <p className="hero-subtitle mb-12 max-w-3xl">
          Visualisez et analysez le réseau Lightning en temps réel
        </p>
      </section>

      {/* Network Stats */}
      <section className="section">
        <div className="glass-card p-8 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <div className="fade-in">
              <div className="text-4xl font-bold text-primary mb-2">24,891</div>
              <div className="text-muted">Nœuds actifs</div>
            </div>
            <div className="fade-in [animation-delay:200ms]">
              <div className="text-4xl font-bold text-primary mb-2">128,450</div>
              <div className="text-muted">Canaux</div>
            </div>
            <div className="fade-in [animation-delay:400ms]">
              <div className="text-4xl font-bold text-primary mb-2">5,234 BTC</div>
              <div className="text-muted">Capacité totale</div>
            </div>
            <div className="fade-in [animation-delay:600ms]">
              <div className="text-4xl font-bold text-primary mb-2">4.2M</div>
              <div className="text-muted">Transactions/jour</div>
            </div>
          </div>
        </div>
      </section>

      {/* Network Map */}
      <section className="section">
        <div className="glass-card p-6 h-[600px] relative overflow-hidden">
          {isLoading ? (
            <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-r from-gradient-start/50 via-gradient-middle/50 to-gradient-end/50 backdrop-blur-sm">
              <div className="text-center">
                <Zap className="h-12 w-12 text-primary animate-pulse mx-auto mb-4" />
                <p className="text-muted">Chargement de la carte du réseau...</p>
              </div>
            </div>
          ) : null}
          <div id="network-map" className="w-full h-full" />
        </div>
      </section>

      {/* Network Actions */}
      <section className="section">
        <div className="content-grid">
          <div className="glass-card p-6 fade-in group hover:bg-white/5 transition-colors">
            <Search className="h-8 w-8 text-primary mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-xl font-semibold mb-4">Analyse de Nœud</h3>
            <p className="text-muted mb-4">Examinez les métriques détaillées de n'importe quel nœud du réseau</p>
            <button className="btn-primary w-full">Analyser un nœud</button>
          </div>
          <div className="glass-card p-6 fade-in [animation-delay:200ms] group hover:bg-white/5 transition-colors">
            <Zap className="h-8 w-8 text-primary mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-xl font-semibold mb-4">Recherche de Route</h3>
            <p className="text-muted mb-4">Trouvez le chemin optimal entre deux nœuds du réseau</p>
            <button className="btn-primary w-full">Chercher une route</button>
          </div>
          <div className="glass-card p-6 fade-in [animation-delay:400ms] group hover:bg-white/5 transition-colors">
            <BarChart3 className="h-8 w-8 text-primary mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-xl font-semibold mb-4">Statistiques Avancées</h3>
            <p className="text-muted mb-4">Accédez aux statistiques détaillées du réseau Lightning</p>
            <button className="btn-primary w-full">Voir les stats</button>
          </div>
        </div>
      </section>
    </>
  );
} 