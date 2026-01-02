import React from 'react';

interface AuthCardProps {
  children: React.ReactNode;
}

export function AuthCard({ children }: AuthCardProps) {
  return (
    <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-800 py-8 px-4 shadow-xl sm:rounded-2xl sm:px-10 transition-all duration-300">
      {children}
    </div>
  );
}
