import { ClipboardIcon, QrCodeIcon } from '@heroicons/react/24/outline';
import { NodeData } from '@/lib/types/node';

interface NodeIdentifiersProps {
  nodeData: NodeData;
}

export default function NodeIdentifiers({ nodeData }: NodeIdentifiersProps) {
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // Idéalement ajouter une notification toast ici
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {nodeData.identifiers.torAddress && (
        <div className="card p-4">
          <h3 className="text-lg font-medium mb-2">Tor Address</h3>
          <div className="flex items-center space-x-2">
            <div className="bg-card-dark border border-gray-700 rounded-md p-2 flex-grow">
              <p className="font-mono text-sm truncate">{nodeData.identifiers.torAddress}</p>
            </div>
            <button
              onClick={() => copyToClipboard(nodeData.identifiers.torAddress || '')}
              className="p-2 bg-gray-800 rounded-md hover:bg-gray-700"
              title="Copier"
            >
              <ClipboardIcon className="h-5 w-5" />
            </button>
            <button
              className="p-2 bg-gray-800 rounded-md hover:bg-gray-700"
              title="Afficher QR Code"
            >
              <QrCodeIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      )}

      {nodeData.identifiers.link && (
        <div className="card p-4">
          <h3 className="text-lg font-medium mb-2">Link</h3>
          <div className="flex items-center space-x-2">
            <div className="bg-card-dark border border-gray-700 rounded-md p-2 flex-grow">
              <p className="font-mono text-sm truncate">{nodeData.identifiers.link}</p>
            </div>
            <button
              onClick={() => copyToClipboard(nodeData.identifiers.link || '')}
              className="p-2 bg-gray-800 rounded-md hover:bg-gray-700"
              title="Copier"
            >
              <ClipboardIcon className="h-5 w-5" />
            </button>
            <button
              className="p-2 bg-gray-800 rounded-md hover:bg-gray-700"
              title="Afficher QR Code"
            >
              <QrCodeIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
} 