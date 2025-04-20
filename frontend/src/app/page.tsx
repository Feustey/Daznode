'use client';

import { Suspense } from 'react';
import NavBar from '@/components/layout/NavBar';
import NodeDashboard from '@/components/ui/NodeDashboard';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { useNode } from '@/lib/contexts/NodeContext';

export default function Home() {
  const { pubkey } = useNode();

  return (
    <main className="min-h-screen">
      <NavBar />
      <Suspense fallback={<LoadingSpinner />}>
        <NodeDashboard pubkey={pubkey} />
      </Suspense>
    </main>
  );
}
