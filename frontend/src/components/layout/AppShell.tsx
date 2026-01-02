import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';

export function AppShell() {
  return (
    <div className="flex h-screen bg-bg-dark text-white overflow-hidden font-sans selection:bg-primary-start/30">
      <Sidebar />
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        <Outlet />
      </main>
    </div>
  );
}
