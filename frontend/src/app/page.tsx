'use client';

import { Suspense } from 'react';
import NavBar from '@/components/layout/NavBar';
import Hero from '@/components/ui/Hero';
import NodeDashboard from '@/components/ui/NodeDashboard';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { useNode } from '@/lib/contexts/NodeContext';

export default function Home() {
  const { pubkey } = useNode();

  return (
    <>
      {/* Hero Section */}
      <section className="section min-h-[80vh] flex flex-col items-center justify-center text-center">
        <h1 className="hero-title mb-6">
          Gérez vos nœuds<br />
          Lightning Network en<br />
          toute simplicité
        </h1>
        <p className="hero-subtitle mb-12 max-w-3xl">
          Optimisez vos performances et votre rentabilité avec Daznode
        </p>
        <div className="flex gap-6">
          <a href="/get-started" className="btn-primary">
            Obtenez votre Dazbox !
          </a>
          <a href="/learn" className="btn-primary bg-opacity-10 hover:bg-opacity-20">
            Apprentissage
          </a>
        </div>
      </section>

      {/* Features Section */}
      <section className="section">
        <div className="content-grid">
          <div className="glass-card p-6 fade-in">
            <h3 className="text-xl font-semibold mb-4">Monitoring en temps réel</h3>
            <p className="text-muted">Surveillez vos canaux et votre liquidité en un coup d'œil</p>
          </div>
          <div className="glass-card p-6 fade-in [animation-delay:200ms]">
            <h3 className="text-xl font-semibold mb-4">Gestion automatisée</h3>
            <p className="text-muted">Optimisez vos frais et votre routage automatiquement</p>
          </div>
          <div className="glass-card p-6 fade-in [animation-delay:400ms]">
            <h3 className="text-xl font-semibold mb-4">Analyses détaillées</h3>
            <p className="text-muted">Prenez des décisions éclairées grâce à nos analyses avancées</p>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="section">
        <div className="glass-card p-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-primary mb-2">1000+</div>
              <div className="text-muted">Nœuds actifs</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary mb-2">₿ 150+</div>
              <div className="text-muted">Capacité totale</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary mb-2">99.9%</div>
              <div className="text-muted">Disponibilité</div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
