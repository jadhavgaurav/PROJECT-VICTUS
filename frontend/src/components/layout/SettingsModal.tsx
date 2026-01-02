import { useState, useEffect } from 'react';
import { X, User, Shield, Brain, Trash2, Check, AlertCircle, LogOut } from 'lucide-react';
import clsx from 'clsx';
import { apiClient } from '../../api/client';
import { useAuth } from '../../context/AuthContext';


interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type Tab = 'general' | 'memory' | 'security';

export function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<Tab>('general');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  // Security State
  const [passwords, setPasswords] = useState({ current: '', new: '', confirm: '' });
  
  // Memory State
  const [facts, setFacts] = useState<any[]>([]);

  useEffect(() => {
    if (isOpen && activeTab === 'memory') {
      loadFacts();
    }
    setMessage(null);
  }, [isOpen, activeTab]);

  async function loadFacts() {
    try {
      setIsLoading(true);
      const res = await apiClient.get('/api/facts');
      setFacts(res.data.facts);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }

  async function deleteFact(id: number) {
    try {
      await apiClient.delete(`/api/facts/${id}`);
      setFacts(facts.filter(f => f.id !== id));
    } catch (err) {
      console.error(err);
    }
  }

  async function updatePassword() {
    if (passwords.new !== passwords.confirm) {
      setMessage({ type: 'error', text: "New passwords don't match" });
      return;
    }
    
    try {
      setIsLoading(true);
      await apiClient.post('/api/auth/change-password', {
        current_password: passwords.current,
        new_password: passwords.new
      });
      setMessage({ type: 'success', text: "Password updated successfully" });
      setPasswords({ current: '', new: '', confirm: '' });
    } catch (err: any) {
      setMessage({ type: 'error', text: err.response?.data?.detail || "Failed to update password" });
    } finally {
      setIsLoading(false);
    }
  }

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-gray-900 border border-gray-800 rounded-xl w-full max-w-3xl h-[600px] flex overflow-hidden shadow-2xl">
        
        {/* Sidebar */}
        <div className="w-64 bg-gray-950 border-r border-gray-800 p-4 flex flex-col justify-between">
            <div>
              <h2 className="text-lg font-bold text-white mb-6 px-2">Settings</h2>
              <nav className="space-y-1">
                <button
                  onClick={() => setActiveTab('general')}
                  className={clsx(
                    "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                    activeTab === 'general' ? "bg-gray-800 text-white" : "text-gray-400 hover:bg-gray-800/50 hover:text-white"
                  )}
                >
                  <User size={18} />
                  General
                </button>
                <button
                  onClick={() => setActiveTab('memory')}
                  className={clsx(
                    "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                    activeTab === 'memory' ? "bg-gray-800 text-white" : "text-gray-400 hover:bg-gray-800/50 hover:text-white"
                  )}
                >
                  <Brain size={18} />
                  Memory
                </button>
                <button
                  onClick={() => setActiveTab('security')}
                  className={clsx(
                    "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                    activeTab === 'security' ? "bg-gray-800 text-white" : "text-gray-400 hover:bg-gray-800/50 hover:text-white"
                  )}
                >
                  <Shield size={18} />
                  Security
                </button>
              </nav>
            </div>

            {/* Logout button at bottom of sidebar */}
             <button
                onClick={logout}
                className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-red-400 hover:bg-red-500/10 transition-colors"
              >
                <LogOut size={18} />
                Log out
              </button>
        </div>

        {/* Content */}
        <div className="flex-1 flex flex-col min-w-0">
          <div className="flex justify-between items-center p-6 border-b border-gray-800">
            <h3 className="text-xl font-semibold text-white capitalize">{activeTab}</h3>
            <button onClick={onClose} className="text-gray-400 hover:text-white">
              <X size={24} />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-6">
            {message && (
              <div className={clsx(
                "mb-4 p-3 rounded-lg text-sm flex items-center gap-2",
                message.type === 'success' ? "bg-green-500/10 text-green-400 border border-green-500/20" : "bg-red-500/10 text-red-400 border border-red-500/20"
              )}>
                {message.type === 'success' ? <Check size={16} /> : <AlertCircle size={16} />}
                {message.text}
              </div>
            )}

            {activeTab === 'general' && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Avatar</label>
                  <div className="flex items-center gap-4">
                    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary-start to-primary-end flex items-center justify-center text-white text-2xl font-bold">
                        {user?.username?.charAt(0).toUpperCase()}
                    </div>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Username</label>
                  <input type="text" value={user?.username} disabled className="w-full bg-gray-800 border-gray-700 rounded-lg px-3 py-2 text-gray-300 cursor-not-allowed" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Email</label>
                  <input type="text" value={user?.email} disabled className="w-full bg-gray-800 border-gray-700 rounded-lg px-3 py-2 text-gray-300 cursor-not-allowed" />
                </div>
              </div>
            )}

            {activeTab === 'memory' && (
              <div className="space-y-4">
                <p className="text-sm text-gray-400">
                  Manage the facts and memories the AI has stored about you. Deleting them will make the AI forget this information.
                </p>
                {isLoading && <div className="text-gray-500 italic">Loading memories...</div>}
                
                {!isLoading && facts.length === 0 && (
                   <div className="text-gray-500 italic p-4 text-center border border-gray-800 rounded-lg bg-gray-800/50">
                      No memories stored yet.
                   </div>
                )}

                <div className="space-y-2">
                  {facts.map((fact) => (
                    <div key={fact.id} className="flex items-start justify-between bg-gray-800/50 border border-gray-800 p-3 rounded-lg group hover:border-gray-700 transition-colors">
                      <div>
                        <div className="font-medium text-gray-200">{fact.key}</div>
                        <div className="text-sm text-gray-400">{fact.value}</div>
                      </div>
                      <button 
                        onClick={() => deleteFact(fact.id)}
                        className="text-gray-500 hover:text-red-400 p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                        title="Forget this memory"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="space-y-6 max-w-sm">
                 <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Current Password</label>
                  <input 
                    type="password" 
                    value={passwords.current}
                    onChange={e => setPasswords({...passwords, current: e.target.value})}
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:ring-1 focus:ring-primary-start outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">New Password</label>
                  <input 
                     type="password" 
                     value={passwords.new}
                     onChange={e => setPasswords({...passwords, new: e.target.value})}
                     className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:ring-1 focus:ring-primary-start outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Confirm New Password</label>
                  <input 
                     type="password" 
                     value={passwords.confirm}
                     onChange={e => setPasswords({...passwords, confirm: e.target.value})}
                     className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:ring-1 focus:ring-primary-start outline-none"
                  />
                </div>
                <button 
                  onClick={updatePassword}
                  disabled={isLoading || !passwords.current || !passwords.new}
                  className="w-full py-2 bg-primary-start hover:bg-primary-end text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Updating...' : 'Update Password'}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
