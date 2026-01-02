import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { AuthLayout } from '../components/auth/AuthLayout';
import { AuthCard } from '../components/auth/AuthCard';
import { TextField } from '../components/auth/TextField';
import { OAuthButton } from '../components/auth/OAuthButton';
import { AlertCircle, Eye, EyeOff, Loader2 } from 'lucide-react';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  // Simple validation state
  // In a larger app, use react-hook-form + zod
  const isFormValid = email && password.length >= 1;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email || !password) return;

    try {
      setError('');
      setIsLoading(true);
      await login({ email, password });
      navigate('/');
    } catch (err: any) {
      if (err.response?.status === 401) {
        setError('Invalid email or password.');
      } else {
        setError('Something went wrong. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  }

  const handleOAuthLogin = (provider: 'google' | 'microsoft') => {
    // Use relative path to leverage Vite proxy
    window.location.href = `/api/auth/oauth/${provider}/start`;
  };

  return (
    <AuthLayout subtitle="Sign in to your account">
      <AuthCard>
        <form className="space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md bg-red-50 p-4 border border-red-200">
              <div className="flex">
                <div className="flex-shrink-0">
                  <AlertCircle className="h-5 w-5 text-red-400" aria-hidden="true" />
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">{error}</h3>
                </div>
              </div>
            </div>
          )}

          <TextField
            id="email"
            type="email"
            label="Email address"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
          />

          <div>
             <TextField
              id="password"
              type={showPassword ? 'text' : 'password'}
              label="Password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              endAdornment={
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="rounded-full p-1 text-gray-400 hover:text-gray-500 hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" aria-hidden="true" />
                  ) : (
                    <Eye className="h-4 w-4" aria-hidden="true" />
                  )}
                </button>
              }
            />
            <div className="flex items-center justify-end mt-1">
              <div className="text-sm">
                <Link to="/forgot-password" className="font-medium text-indigo-400 hover:text-indigo-300">
                  Forgot password?
                </Link>
              </div>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={!isFormValid || isLoading}
              className="flex w-full justify-center items-center gap-2 rounded-xl bg-gradient-to-r from-primary-start to-primary-end px-3 py-2 text-sm font-semibold text-white shadow-lg shadow-primary-start/20 hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              {isLoading ? (
                 <>
                   <Loader2 className="h-4 w-4 animate-spin" />
                   Signing in...
                 </>
              ) : (
                'Sign in'
              )}
            </button>
          </div>
        </form>

        <div className="mt-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-700" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-gray-900 px-2 text-gray-400">Or continue with</span>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-1 gap-3">
            <OAuthButton provider="google" onClick={() => handleOAuthLogin('google')} />
            <OAuthButton provider="microsoft" onClick={() => handleOAuthLogin('microsoft')} />
          </div>
        </div>

        <p className="mt-6 text-center text-sm text-gray-400">
          Don't have an account?{' '}
          <Link to="/signup" className="font-semibold leading-6 text-indigo-400 hover:text-indigo-300">
            Sign up
          </Link>
        </p>
      </AuthCard>
    </AuthLayout>
  );
}
