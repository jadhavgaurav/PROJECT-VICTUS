import { useState, useEffect } from 'react';
import { BarChart2 } from 'lucide-react';
import { Skeleton } from '../ui/Skeleton';

export function AnalyticsDashboard() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 2500); // Simulate fetch
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
      return (
          <div className="p-8 h-full">
            <h2 className="text-xl font-bold mb-6">Analytics Dashboard</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Skeleton height={300} className="w-full" />
                <Skeleton height={300} className="w-full" />
                <Skeleton height={300} className="w-full" />
                <Skeleton height={300} className="w-full" />
            </div>
          </div>
      );
  }

  return (
    <div className="flex flex-col items-center justify-center h-full text-gray-500 anim-enter">
      <div className="bg-gray-800 p-4 rounded-full mb-4 anim-scale-in">
        <BarChart2 size={48} className="text-gray-400" />
      </div>
      <h2 className="text-xl font-semibold text-gray-200 mb-2">Analytics Dashboard</h2>
      <p className="max-w-md text-center">
        Visualize agent performance, latency, and tool usage metrics over time.
      </p>
    </div>
  );
}

