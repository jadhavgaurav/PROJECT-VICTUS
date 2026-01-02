import { useState, useEffect, useRef } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { MessageSquare, CheckSquare, Activity, BarChart2, Image, Plus, Trash2, LogOut, Settings } from 'lucide-react';
import clsx from 'clsx';
import { apiClient } from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import { Modal } from '../ui/Modal';
import { SettingsModal } from './SettingsModal';

// ... (navItems array remains same, but we can reuse existing constants if not deleting)
const navItems = [
  { to: '/approvals', icon: CheckSquare, label: 'Approvals' },
  { to: '/traces', icon: Activity, label: 'Traces' },
  { to: '/analytics', icon: BarChart2, label: 'Analytics' },
  { to: '/visuals', icon: Image, label: 'Visuals' },
];

interface Conversation {
  id: string;
  title: string;
  updated_at: string;
}

export function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  
  // Settings & Dropdown State
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const profileMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadConversations();
    const interval = setInterval(loadConversations, 10000);
    
    // Close dropdown on click outside
    const handleClickOutside = (event: MouseEvent) => {
      if (profileMenuRef.current && !profileMenuRef.current.contains(event.target as Node)) {
        setIsProfileMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    
    return () => {
      clearInterval(interval);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  async function loadConversations() {
    try {
      const res = await apiClient.get('/api/conversations?limit=20');
      setConversations(res.data);
    } catch (err) {
      console.error("Failed to load conversations", err);
    }
  }

  async function createNewChat() {
    navigate('/');
  }

  function confirmDelete(e: React.MouseEvent, id: string) {
    e.preventDefault();
    e.stopPropagation();
    setDeleteId(id);
  }

  async function handleDelete() {
    if (!deleteId) return;
    try {
      await apiClient.delete(`/api/conversations/${deleteId}`);
      loadConversations();
      if (window.location.pathname === `/c/${deleteId}`) {
        navigate('/');
      }
      setDeleteId(null);
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <aside className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col h-screen">
      <div className="p-6 border-b border-gray-800 flex justify-between items-center">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-start to-primary-end bg-clip-text text-transparent cursor-pointer" onClick={() => navigate('/')}>
          VICTUS
        </h1>
        <button onClick={createNewChat} className="p-1 hover:bg-gray-800 rounded text-gray-400 hover:text-white" title="New Chat">
          <Plus size={20} />
        </button>
      </div>
      
      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-1">
        <div className="text-xs font-semibold text-gray-500 px-4 py-2 uppercase">Recent Chats</div>
        {conversations.map((conv) => (
          <NavLink
            key={conv.id}
            to={`/c/${conv.id}`}
            className={({ isActive }) =>
              clsx(
                'group flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors',
                isActive
                  ? 'bg-gray-800 text-white'
                  : 'text-gray-400 hover:bg-gray-800/50 hover:text-gray-200'
              )
            }
          >
            <div className="flex items-center gap-2 truncate">
              <MessageSquare size={16} />
              <span className="truncate max-w-[120px]">{conv.title}</span>
            </div>
            <button 
                onClick={(e) => confirmDelete(e, conv.id)}
                className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-400"
            >
                <Trash2 size={14} />
            </button>
          </NavLink>
        ))}
      </div>

      <div className="p-2 space-y-1 border-t border-gray-800">
        <div className="text-xs font-semibold text-gray-500 px-4 py-2 uppercase">Tools</div>
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
                isActive
                  ? 'bg-primary-start/10 text-primary-start border border-primary-start/20'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'
              )
            }
          >
            <item.icon size={18} />
            <span className="font-medium">{item.label}</span>
          </NavLink>
        ))}
      </div>
      
      {/* User Profile with Popup Trigger */}
      <div className="py-4 px-4 border-t border-gray-800 relative" ref={profileMenuRef}>
        {isProfileMenuOpen && (
           <div className="absolute bottom-[calc(100%-10px)] left-4 w-[220px] bg-gray-900 border border-gray-700 rounded-xl shadow-xl overflow-hidden z-20 animate-fade-in-up">
              <div className="p-1">
                 <button 
                    onClick={() => { setIsSettingsOpen(true); setIsProfileMenuOpen(false); }}
                    className="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-gray-300 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
                 >
                    <Settings size={16} />
                    Settings
                 </button>
                 <div className="h-px bg-gray-800 my-1" />
                 <button 
                    onClick={logout}
                    className="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors"
                 >
                    <LogOut size={16} />
                    Log out
                 </button>
              </div>
           </div>
        )}

        <button 
            onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
            className="w-full flex items-center justify-between gap-3 px-2 py-2 rounded-lg hover:bg-gray-800 transition-colors"
        >
            <div className="flex items-center gap-3 overflow-hidden">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-start to-primary-end flex items-center justify-center text-white font-bold text-sm shrink-0">
                    {user?.username?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div className="overflow-hidden text-left">
                    <p className="text-sm font-medium text-white truncate">{user?.username}</p>
                    <p className="text-xs text-gray-500 truncate max-w-[120px]">{user?.email}</p>
                </div>
            </div>
        </button>
      </div>

      <Modal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        title="Delete Conversation"
      >
        <p className="text-gray-300 mb-6">
          Are you sure you want to delete this conversation? This action cannot be undone.
        </p>
        <div className="flex justify-end gap-3">
          <button
            onClick={() => setDeleteId(null)}
            className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleDelete}
            className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
          >
            Delete
          </button>
        </div>
      </Modal>

      <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
    </aside>
  );
}
