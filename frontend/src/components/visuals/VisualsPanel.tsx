import { useState, useEffect } from 'react';
import { Image } from 'lucide-react';
import { Skeleton } from '../ui/Skeleton';

export function VisualsPanel() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 1800); // Simulate fetch
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
      return (
          <div className="p-8 h-full">
            <h2 className="text-xl font-bold mb-6">Visuals Gallery</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Skeleton height={200} className="w-full" />
                <Skeleton height={200} className="w-full" />
                <Skeleton height={200} className="w-full" />
            </div>
          </div>
      );
  }

  return (
    <div className="flex flex-col items-center justify-center h-full text-gray-500 anim-enter">
      <div className="bg-gray-800 p-4 rounded-full mb-4 anim-scale-in">
        <Image size={48} className="text-gray-400" />
      </div>
      <h2 className="text-xl font-semibold text-gray-200 mb-2">Visuals Gallery</h2>
      <p className="max-w-md text-center">
        Generate Mermaid diagrams and Vega-Lite charts from your data and prompts.
      </p>
    </div>
  );
}

