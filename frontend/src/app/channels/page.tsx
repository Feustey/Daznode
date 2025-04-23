'use client';

import { ArrowLeftRight, Zap, Wallet } from 'lucide-react';

export default function ChannelsPage() {
  return (
    <>
      {/* Hero Section */}
      <section className="section min-h-[40vh] flex flex-col items-center justify-center text-center">
        <h1 className="hero-title mb-6">
          Gestion des Canaux
        </h1>
        <p className="hero-subtitle mb-12 max-w-3xl">
          Optimisez vos canaux Lightning pour une meilleure performance
        </p>
      </section>

      {/* Channel Stats */}
      <section className="section">
        <div className="glass-card p-8 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div className="fade-in">
              <div className="text-4xl font-bold text-primary mb-2">42</div>
              <div className="text-muted">Canaux actifs</div>
            </div>
            <div className="fade-in [animation-delay:200ms]">
              <div className="text-4xl font-bold text-primary mb-2">2.5 BTC</div>
              <div className="text-muted">Capacité totale</div>
            </div>
            <div className="fade-in [animation-delay:400ms]">
              <div className="text-4xl font-bold text-primary mb-2">98.5%</div>
              <div className="text-muted">Disponibilité</div>
            </div>
          </div>
        </div>
      </section>

      {/* Channel List */}
      <section className="section">
        <div className="glass-card p-6 overflow-hidden">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-semibold">Vos Canaux</h2>
            <button className="btn-primary">
              <Zap className="h-4 w-4 mr-2 inline" />
              Ouvrir un canal
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left border-b border-border">
                  <th className="pb-4 font-medium text-muted">Pair</th>
                  <th className="pb-4 font-medium text-muted">Capacité</th>
                  <th className="pb-4 font-medium text-muted">Balance Locale</th>
                  <th className="pb-4 font-medium text-muted">État</th>
                  <th className="pb-4 font-medium text-muted">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-border/50 hover:bg-white/5">
                  <td className="py-4">ACINQ</td>
                  <td className="py-4">0.5 BTC</td>
                  <td className="py-4">0.3 BTC</td>
                  <td className="py-4">
                    <span className="px-2 py-1 rounded-full bg-green-500/20 text-green-400 text-sm">
                      Actif
                    </span>
                  </td>
                  <td className="py-4">
                    <button className="text-muted hover:text-white transition-colors">
                      Gérer
                    </button>
                  </td>
                </tr>
                {/* Ajoutez plus de lignes ici */}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Channel Actions */}
      <section className="section">
        <div className="content-grid">
          <div className="glass-card p-6 fade-in group hover:bg-white/5 transition-colors">
            <Zap className="h-8 w-8 text-primary mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-xl font-semibold mb-4">Ouverture Automatique</h3>
            <p className="text-muted mb-4">Laissez Daznode ouvrir automatiquement les meilleurs canaux</p>
            <button className="btn-primary w-full">Configurer</button>
          </div>
          <div className="glass-card p-6 fade-in [animation-delay:200ms] group hover:bg-white/5 transition-colors">
            <ArrowLeftRight className="h-8 w-8 text-primary mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-xl font-semibold mb-4">Rééquilibrage</h3>
            <p className="text-muted mb-4">Optimisez la liquidité de vos canaux automatiquement</p>
            <button className="btn-primary w-full">Rééquilibrer</button>
          </div>
          <div className="glass-card p-6 fade-in [animation-delay:400ms] group hover:bg-white/5 transition-colors">
            <Wallet className="h-8 w-8 text-primary mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-xl font-semibold mb-4">Gestion des Frais</h3>
            <p className="text-muted mb-4">Ajustez vos frais pour maximiser vos revenus</p>
            <button className="btn-primary w-full">Gérer les frais</button>
          </div>
        </div>
      </section>
    </>
  );
} 