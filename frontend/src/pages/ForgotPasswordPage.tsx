import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, ArrowLeft, Send } from 'lucide-react';
import { apiClient } from '../api/client';
import { useToast } from '../components/ui/Toasts';
import clsx from 'clsx';

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSent, setIsSent] = useState(false);
  const { showToast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setIsLoading(true);
    try {
      await apiClient.post('/api/auth/forgot-password', { email });
      setIsSent(true);
      showToast({
        type: 'success',
        title: 'Email Sent',
        message: 'If an account exists, you will receive reset instructions.',
      });
    } catch (error) {
      // Error is handled by global interceptor, but we catch here to stop loading state if needed
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto h-12 w-12 bg-gray-900 rounded-xl flex items-center justify-center mb-4">
            <Mail className="h-6 w-6 text-primary-start" />
          </div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
            Forgot Password?
          </h2>
          <p className="mt-2 text-gray-400">
            {isSent 
              ? "Check your email for instructions" 
              : "Enter your email to receive reset instructions"
            }
          </p>
        </div>

        {/* Form or Success State */}
        <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-800 rounded-2xl p-8 shadow-xl">
          {isSent ? (
            <div className="text-center space-y-6">
              <div className="bg-green-500/10 text-green-400 p-4 rounded-xl border border-green-500/20">
                <p className="text-sm">
                  We've sent an email to <strong>{email}</strong>. Please check your inbox and spam folder.
                </p>
              </div>
              <Link 
                to="/login"
                className="block w-full py-3 px-4 bg-gray-800 hover:bg-gray-700 text-white rounded-xl font-medium transition-all"
              >
                Return to Login
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                  Email address
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-950 border border-gray-800 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-start/50 focus:border-primary-start transition-all"
                  placeholder="Enter your email"
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
                    Send Instructions <Send size={18} />
                  </>
                )}
              </button>
            </form>
          )}
        </div>

        {/* Footer */}
        <div className="text-center">
          <Link to="/login" className="inline-flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors">
            <ArrowLeft size={16} /> Back to Login
          </Link>
        </div>
      </div>
    </div>
  );
}
