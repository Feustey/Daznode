import { StarIcon, BellIcon, ClipboardIcon, BoltIcon } from '@heroicons/react/24/solid';
import { formatPubkey } from '@/lib/hooks/useNodeData';
import { NodeData } from '@/lib/types/node';

interface NodeHeaderProps {
  nodeData: NodeData;
  onToggleFavorite?: () => void;
  isFavorite?: boolean;
}

export default function NodeHeader({ nodeData, onToggleFavorite, isFavorite }: NodeHeaderProps) {
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // Idéalement ajouter une notification toast ici
  };

  return (
    <div className="p-6 flex flex-col md:flex-row justify-between items-start md:items-center">
      <div className="flex items-center">
        <div className="flex flex-col">
          <div className="flex items-center">
            <BoltIcon className="h-7 w-7 text-yellow-500" />
            <h1 className="text-2xl font-bold ml-2">{nodeData.alias}</h1>
            <span className="ml-2 text-yellow-500">⚡</span>
            <span className="ml-1 text-blue-500">🚀</span>
          </div>
          
          <div className="flex items-center mt-2">
            <span className="text-gray-400 text-sm font-mono">
              {formatPubkey(nodeData.pubkey)}
            </span>
            <button 
              onClick={() => copyToClipboard(nodeData.pubkey)}
              className="ml-2 text-gray-400 hover:text-white"
            >
              <ClipboardIcon className="h-4 w-4" />
            </button>
          </div>
          
          {nodeData.customTags && nodeData.customTags.length > 0 && (
            <div className="mt-2">
              {nodeData.customTags.map((tag, index) => (
                <span 
                  key={index} 
                  className="bg-purple-900 text-purple-200 px-3 py-1 rounded-full text-sm"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
      
      <div className="flex items-center mt-4 md:mt-0">
        <button 
          onClick={onToggleFavorite}
          className="flex items-center bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-lg mr-4"
        >
          <StarIcon 
            className={`h-5 w-5 ${isFavorite ? 'text-yellow-500' : 'text-gray-400'}`} 
          />
          <span className="ml-2">Favorite</span>
        </button>
        
        <button className="flex items-center bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-lg">
          <BellIcon className="h-5 w-5 text-gray-400" />
          <span className="ml-2">Notifications</span>
          <span className="ml-2 bg-gray-700 px-2 py-0.5 rounded-full text-sm">2</span>
        </button>
      </div>
    </div>
  );
} 