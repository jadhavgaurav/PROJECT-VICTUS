import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { AuthLayout } from '../components/auth/AuthLayout';
import { AuthCard } from '../components/auth/AuthCard';
import { TextField } from '../components/auth/TextField';
import { AlertCircle, Loader2 } from 'lucide-react';
import { apiClient } from '../api/client';

export function CompleteOAuthPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const suggestedUsername = searchParams.get('suggested') || '';
  
  const [username, setUsername] = useState(suggestedUsername);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { checkAuth } = useAuth();
  const navigate = useNavigate();

  // Redirect if no token
  useEffect(() => {
    if (!token) {
        navigate('/login');
    }
  }, [token, navigate]);

  const isFormValid = username.length >= 3;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!username || !token) return;

    try {
      setError('');
      setIsLoading(true);
      
      await apiClient.post('/api/auth/oauth/finalize', {
        token,
        username
      });
      
      // Update global auth state
      await checkAuth();
      
      navigate('/');
    } catch (err: any) {
        console.error("Registration error:", err);
        let msg = err.response?.data?.detail || err.message || 'Registration failed.';
        setError(msg + " (Debug: " + JSON.stringify(err) + ")");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <AuthLayout subtitle="Complete your registration">
      <AuthCard>
        <div className="mb-6 text-center">
            <h2 className="text-lg font-medium text-white">Choose a Username</h2>
            <p className="mt-1 text-sm text-gray-400">
                Please confirm or change your username to finish setting up your account.
            </p>
        </div>

        <form className="space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-xl bg-red-900/10 p-4 border border-red-900/20">
              <div className="flex">
                <div className="flex-shrink-0">
                  <AlertCircle className="h-5 w-5 text-red-400" aria-hidden="true" />
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-200">{error}</h3>
                </div>
              </div>
            </div>
          )}

          <TextField
            id="username"
            type="text"
            label="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoComplete="username"
            placeholder="Choose a username"
          />

          <div>
            <button
              type="submit"
              disabled={!isFormValid || isLoading}
              className="flex w-full justify-center items-center gap-2 rounded-xl bg-gradient-to-r from-primary-start to-primary-end px-3 py-2 text-sm font-semibold text-white shadow-lg shadow-primary-start/20 hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              {isLoading ? (
                 <>
                   <Loader2 className="h-4 w-4 animate-spin" />
                   Creating Account...
                 </>
              ) : (
                'Complete Registration'
              )}
            </button>
          </div>
        </form>
      </AuthCard>
    </AuthLayout>
  );
}
