'use client';

import { Suspense } from 'react';
import NavBar from '@/components/layout/NavBar';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import UnprofitableChannelsTable from '@/components/ui/UnprofitableChannelsTable';

export default function UnprofitableChannelsPage() {
  return (
    <main className="min-h-screen">
      <NavBar />
      <Suspense fallback={<LoadingSpinner />}>
        <div className="container mx-auto p-6">
          <h1 className="text-2xl font-bold mb-6">Canaux Non Rentables</h1>
          <div className="card p-6">
            <UnprofitableChannelsTable />
          </div>
        </div>
      </Suspense>
    </main>
  );
} 