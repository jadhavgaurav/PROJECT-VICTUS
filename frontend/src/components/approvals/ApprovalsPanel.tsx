import { useState, useEffect } from 'react';
import { CheckSquare } from 'lucide-react';
import { useToast } from '../ui/Toasts';
import { Skeleton } from '../ui/Skeleton';


export function ApprovalsPanel() {
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => setLoading(false), 1500);
    return () => clearTimeout(timer);
  }, []);

  const handleAction = (action: 'approve' | 'deny') => {
      showToast({
          type: action === 'approve' ? 'success' : 'error',
          title: action === 'approve' ? 'Action Approved' : 'Action Denied',
          message: action === 'approve' ? 'The requested action has been authorized.' : 'The requested action was blocked.'
      });
  };

  if (loading) {
      return (
          <div className="p-8 max-w-2xl mx-auto w-full">
              <h2 className="text-xl font-bold mb-6">Pending Approvals</h2>
              <div className="space-y-4">
                  <Skeleton height={120} className="w-full" />
                  <Skeleton height={120} className="w-full" />
              </div>
          </div>
      );
  }

  return (
    <div className="flex flex-col items-center justify-center h-full text-gray-500 anim-enter">
      <div className="bg-gray-800 p-4 rounded-full mb-4 anim-scale-in">
        <CheckSquare size={48} className="text-gray-400" />
      </div>
      <h2 className="text-xl font-semibold text-gray-200 mb-2">No Pending Approvals</h2>
      <p className="max-w-md text-center mb-8">
        When the agent needs permission to perform a sensitive action (like file deletion or sending emails), it will appear here.
      </p>
      
      {/* Demo Button for testing Toasts */}
      <button 
        onClick={() => handleAction('approve')}
        className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-sm rounded border border-gray-700 transition-colors"
      >
        Simulate Notification
      </button>
    </div>
  );
}

