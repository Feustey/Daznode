'use client';

import { useEffect, useRef, useState } from 'react';
import { MCPService } from '@/lib/mcp';
import { useNode } from '@/lib/contexts/NodeContext';

interface Node {
  id: string;
  alias: string;
  color: string;
  capacity: number;
}

interface Channel {
  source: string;
  target: string;
  capacity: number;
}

interface NetworkData {
  nodes: Node[];
  channels: Channel[];
}

export default function NetworkGraph() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [data, setData] = useState<NetworkData | null>(null);
  const { pubkey } = useNode();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const mcpService = new MCPService();
        const response = await mcpService.get_network_map();
        
        if (response) {
          setData({
            nodes: response.nodes || [],
            channels: response.channels || [],
          });
        }
      } catch (error) {
        console.error('Erreur lors de la récupération de la carte du réseau:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  useEffect(() => {
    if (!data || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Configuration de base
    const width = canvas.width;
    const height = canvas.height;
    
    // Effacer le canvas
    ctx.clearRect(0, 0, width, height);
    
    // Fonction pour dessiner le réseau
    const drawNetwork = () => {
      // Créer un mapping des nœuds pour un accès rapide
      const nodeMap = new Map();
      data.nodes.forEach((node, index) => {
        // Positionnement aléatoire des nœuds
        const x = 50 + Math.random() * (width - 100);
        const y = 50 + Math.random() * (height - 100);
        
        nodeMap.set(node.id, { 
          ...node, 
          x, 
          y, 
          radius: Math.max(3, Math.min(10, node.capacity / 10000000))
        });
      });
      
      // Dessiner les canaux
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
      ctx.lineWidth = 0.5;
      
      data.channels.forEach(channel => {
        const source = nodeMap.get(channel.source);
        const target = nodeMap.get(channel.target);
        
        if (source && target) {
          ctx.beginPath();
          ctx.moveTo(source.x, source.y);
          ctx.lineTo(target.x, target.y);
          ctx.stroke();
        }
      });
      
      // Dessiner les nœuds
      nodeMap.forEach(node => {
        ctx.beginPath();
        
        // Nœud actuel en surbrillance
        if (node.id === pubkey) {
          ctx.fillStyle = '#ffffff';
          ctx.arc(node.x, node.y, node.radius + 2, 0, Math.PI * 2);
          ctx.fill();
        }
        
        ctx.fillStyle = node.color || '#3498db';
        ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
        ctx.fill();
      });
    };
    
    drawNetwork();
  }, [data, pubkey]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-12 text-gray-400">
        Impossible de charger les données du réseau
      </div>
    );
  }

  return (
    <div className="relative h-96">
      <canvas 
        ref={canvasRef}
        className="w-full h-full bg-gray-800 rounded-lg"
        width={800}
        height={600}
      />
      <div className="absolute bottom-2 left-2 bg-gray-800 bg-opacity-80 p-2 rounded text-xs text-gray-300">
        <div className="flex items-center gap-2 mb-1">
          <span className="inline-block w-2 h-2 rounded-full bg-white"></span>
          <span>Votre nœud</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-full bg-blue-500"></span>
          <span>Autres nœuds</span>
        </div>
        <p className="mt-1 text-gray-400">
          {data.nodes.length} nœuds, {data.channels.length} canaux
        </p>
      </div>
    </div>
  );
} 