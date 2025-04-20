import { getMockNodeData } from '@/lib/api/nodeApi';
import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { pubkey: string } }
) {
  try {
    const pubkey = params.pubkey;
    
    // Ici, on utiliserait un service pour récupérer les données réelles du nœud
    // Mais pour le développement, utilisons les données mockées
    const nodeData = getMockNodeData(pubkey);
    
    return NextResponse.json(nodeData);
  } catch (error) {
    console.error('Erreur lors de la récupération des données du nœud:', error);
    return NextResponse.json(
      { error: 'Erreur lors de la récupération des données du nœud' },
      { status: 500 }
    );
  }
} 