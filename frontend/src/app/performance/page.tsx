'use client';

import { LineChart, Activity, TrendingUp } from 'lucide-react';

export default function PerformancePage() {
  return (
    <>
      {/* Hero Section */}
      <section className="section min-h-[40vh] flex flex-col items-center justify-center text-center">
        <h1 className="hero-title mb-6">
          Performance
        </h1>
        <p className="hero-subtitle mb-12 max-w-3xl">
          Analysez et optimisez les performances de votre nœud
        </p>
      </section>

      {/* Performance Metrics */}
      <section className="section">
        <div className="glass-card p-8 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div className="fade-in">
              <div className="text-4xl font-bold text-primary mb-2">1,245</div>
              <div className="text-muted">Transactions routées</div>
            </div>
            <div className="fade-in [animation-delay:200ms]">
              <div className="text-4xl font-bold text-primary mb-2">0.015 BTC</div>
              <div className="text-muted">Revenus ce mois</div>
            </div>
            <div className="fade-in [animation-delay:400ms]">
              <div className="text-4xl font-bold text-primary mb-2">94.8%</div>
              <div className="text-muted">Taux de succès</div>
            </div>
          </div>
        </div>
      </section>

      {/* Charts Section */}
      <section className="section">
        <div className="glass-card p-6 h-[400px] mb-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-semibold">Revenus journaliers</h2>
            <select className="bg-white/5 border border-border rounded-md px-3 py-1 text-sm">
              <option>7 derniers jours</option>
              <option>30 derniers jours</option>
              <option>3 derniers mois</option>
            </select>
          </div>
          <div className="w-full h-[300px] flex items-center justify-center text-muted">
            Graphique des revenus à implémenter
          </div>
        </div>
      </section>

      {/* Performance Actions */}
      <section className="section">
        <div className="content-grid">
          <div className="glass-card p-6 fade-in group hover:bg-white/5 transition-colors">
            <Activity className="h-8 w-8 text-primary mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-xl font-semibold mb-4">Analyse des Flux</h3>
            <p className="text-muted mb-4">Visualisez les flux de paiements à travers votre nœud</p>
            <button className="btn-primary w-full">Voir l'analyse</button>
          </div>
          <div className="glass-card p-6 fade-in [animation-delay:200ms] group hover:bg-white/5 transition-colors">
            <LineChart className="h-8 w-8 text-primary mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-xl font-semibold mb-4">Rapports Détaillés</h3>
            <p className="text-muted mb-4">Accédez à des rapports détaillés sur vos performances</p>
            <button className="btn-primary w-full">Voir les rapports</button>
          </div>
          <div className="glass-card p-6 fade-in [animation-delay:400ms] group hover:bg-white/5 transition-colors">
            <TrendingUp className="h-8 w-8 text-primary mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-xl font-semibold mb-4">Optimisation</h3>
            <p className="text-muted mb-4">Recevez des recommandations pour améliorer vos performances</p>
            <button className="btn-primary w-full">Optimiser</button>
          </div>
        </div>
      </section>
    </>
  );
} 