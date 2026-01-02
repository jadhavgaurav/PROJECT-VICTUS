import React from 'react';
import { Bot, Sparkles } from 'lucide-react';

interface AuthLayoutProps {
  children: React.ReactNode;
  subtitle?: string;
}

export function AuthLayout({ children, subtitle }: AuthLayoutProps) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-950 p-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background Decor */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
          <div className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-indigo-500/10 blur-3xl opacity-20" />
          <div className="absolute top-[40%] right-[10%] w-[40%] h-[40%] rounded-full bg-blue-500/10 blur-3xl opacity-20" />
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10 mb-8">
        <div className="flex justify-center mb-4">
            <div className="p-3 bg-gray-900 rounded-xl shadow-lg ring-1 ring-gray-800">
                <Bot className="h-10 w-10 text-indigo-400" strokeWidth={1.5} />
            </div>
        </div>
        <h2 className="text-center text-3xl font-bold tracking-tight text-white flex items-center justify-center gap-2">
          PROJECT-VICTUS <Sparkles className="h-5 w-5 text-amber-400" fill="currentColor" />
        </h2>
        <p className="mt-2 text-center text-sm text-gray-400">
          {subtitle || "Your AI workspace assistant"}
        </p>
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10">
        {children}
      </div>
    </div>
  );
}
