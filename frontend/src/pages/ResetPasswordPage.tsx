import { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Lock, ArrowLeft, CheckCircle } from 'lucide-react';
import { apiClient } from '../api/client';
import { useToast } from '../components/ui/Toasts';
import clsx from 'clsx';

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const navigate = useNavigate();
  const { showToast } = useToast();

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!token) {
        showToast({ type: 'error', message: 'Missing reset token' });
        navigate('/login');
    }
  }, [token, navigate, showToast]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!password || !token) return;

    if (password !== confirmPassword) {
      showToast({ type: 'error', message: 'Passwords do not match' });
      return;
    }

    if (password.length < 8) {
      showToast({ type: 'error', message: 'Password must be at least 8 characters' });
      return;
    }

    setIsLoading(true);
    try {
      await apiClient.post('/api/auth/reset-password', { 
        token, 
        new_password: password 
      });
      
      showToast({
        type: 'success',
        title: 'Success',
        message: 'Password reset successfully. Please login.',
      });
      navigate('/login');
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!token) return null;

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 bg-gray-900 rounded-xl flex items-center justify-center mb-4">
            <Lock className="h-6 w-6 text-primary-start" />
          </div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
            Set New Password
          </h2>
          <p className="mt-2 text-gray-400">
            Create a strong password for your account
          </p>
        </div>

        <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-800 rounded-2xl p-8 shadow-xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                New Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-gray-950 border border-gray-800 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-start/50 focus:border-primary-start transition-all"
                placeholder="••••••••"
                required
                disabled={isLoading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Confirm Password
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-3 bg-gray-950 border border-gray-800 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-start/50 focus:border-primary-start transition-all"
                placeholder="••••••••"
                required
                disabled={isLoading}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className={clsx(
                "w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-white font-medium transition-all",
                isLoading
                  ? "bg-gray-800 cursor-not-allowed"
                  : "bg-gradient-to-r from-primary-start to-primary-end hover:opacity-90 shadow-lg shadow-primary-start/20"
              )}
            >
              {isLoading ? (
                <span className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  Reset Password <CheckCircle size={18} />
                </>
              )}
            </button>
          </form>
        </div>

        <div className="text-center">
          <Link to="/login" className="inline-flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors">
            <ArrowLeft size={16} /> Back to Login
          </Link>
        </div>
      </div>
    </div>
  );
}
