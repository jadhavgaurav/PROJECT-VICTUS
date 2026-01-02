import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import { X, CheckCircle, Info, AlertTriangle, AlertCircle } from 'lucide-react';
import clsx from 'clsx';

export type ToastType = 'success' | 'info' | 'warning' | 'error';

export interface Toast {
  id: string;
  type: ToastType;
  title?: string;
  message: string;
}

interface ToastContextValue {
  showToast: (props: Omit<Toast, 'id'>) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((props: Omit<Toast, 'id'>) => {
    const id = Date.now().toString();
    const newToast = { ...props, id };
    setToasts((prev) => [...prev, newToast]);

    // Auto dismiss
    setTimeout(() => {
      removeToast(id);
    }, 5000);
    setTimeout(() => {
      removeToast(id);
    }, 5000);
  }, []);

  // Listen for global API errors
  useEffect(() => {
    const handleApiError = (event: Event) => {
        const customEvent = event as CustomEvent;
        showToast({
            type: 'error',
            title: customEvent.detail.title || 'Error',
            message: customEvent.detail.message || 'Something went wrong',
        });
    };

    window.addEventListener('api-error', handleApiError);
    return () => window.removeEventListener('api-error', handleApiError);
  }, [showToast]);

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 w-full max-w-sm pointer-events-none">
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onDismiss={() => removeToast(toast.id)} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

function ToastItem({ toast, onDismiss }: { toast: Toast; onDismiss: () => void }) {
  const icons = {
    success: <CheckCircle className="text-emerald-400" size={20} />,
    info: <Info className="text-blue-400" size={20} />,
    warning: <AlertTriangle className="text-yellow-400" size={20} />,
    error: <AlertCircle className="text-red-400" size={20} />,
  };

  const bgColors = {
    success: 'bg-emerald-500/10 border-emerald-500/20',
    info: 'bg-blue-500/10 border-blue-500/20',
    warning: 'bg-yellow-500/10 border-yellow-500/20',
    error: 'bg-red-500/10 border-red-500/20',
  };

  return (
    <div className={clsx(
      "pointer-events-auto flex items-start gap-3 p-4 rounded-lg border shadow-lg backdrop-blur-md anim-toast-enter",
      bgColors[toast.type]
    )}>
      <div className="shrink-0 mt-0.5">{icons[toast.type]}</div>
      <div className="flex-1">
        {toast.title && <h4 className="font-semibold text-sm text-gray-200">{toast.title}</h4>}
        <p className="text-sm text-gray-400">{toast.message}</p>
      </div>
      <button onClick={onDismiss} className="text-gray-500 hover:text-white transition-colors">
        <X size={16} />
      </button>
    </div>
  );
}
