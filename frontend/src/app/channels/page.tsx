'use client';

import { Suspense } from 'react';
import NavBar from '@/components/layout/NavBar';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

export default function ChannelsPage() {
  return (
    <main className="min-h-screen">
      <NavBar />
      <Suspense fallback={<LoadingSpinner />}>
        <div className="container mx-auto p-6">
          <h1 className="text-2xl font-bold mb-6">Channels</h1>
          <div className="card p-6">
            <p>Contenu de la page Channels - À implémenter</p>
          </div>
        </div>
      </Suspense>
    </main>
  );
} 