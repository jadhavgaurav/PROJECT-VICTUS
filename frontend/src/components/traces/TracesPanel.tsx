import { useState, useEffect } from 'react';
import { Activity } from 'lucide-react';
import { Skeleton } from '../ui/Skeleton';

export function TracesPanel() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 2000); // Simulate fetch
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
      return (
          <div className="p-8 h-full">
            <h2 className="text-xl font-bold mb-6">Recent Traces</h2>
            <div className="space-y-3">
                {[1,2,3,4,5].map(i => (
                    <Skeleton key={i} height={60} className="w-full" />
                ))}
            </div>
          </div>
      );
  }

  return (
    <div className="flex flex-col items-center justify-center h-full text-gray-500 anim-enter">
      <div className="bg-gray-800 p-4 rounded-full mb-4 anim-scale-in">
        <Activity size={48} className="text-gray-400" />
      </div>
      <h2 className="text-xl font-semibold text-gray-200 mb-2">Trace Viewer</h2>
      <p className="max-w-md text-center">
        Inspect the detailed execution path, logic, and performance of recent agent interactions here.
      </p>
    </div>
  );
}

