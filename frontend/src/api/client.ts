import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper to get cookie by name
function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
  return null;
}

// Request interceptor to add CSRF token
apiClient.interceptors.request.use((config) => {
  const csrfToken = getCookie('csrf_token');
  if (csrfToken) {
    config.headers['X-CSRF-Token'] = csrfToken;
  }
  return config;
});

// Response interceptor to handle 401 (e.g., redirect to login)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Default error message
    let message = 'An unexpected error occurred';
    
    if (error.response) {
      // Server returned an error response
      const data = error.response.data;
      if (data && data.detail) {
        message = data.detail;
      } else if (data && data.message) {
        message = data.message;
      }
      

      // Handle 401 specifically
      if (error.response.status === 401) {
        // Suppress 401 errors from the session check endpoint
        if (error.config.url?.includes('/auth/me')) {
            return Promise.reject(error);
        }

        // Only redirects if we aren't already on auth pages
        if (window.location.pathname !== '/login' && window.location.pathname !== '/signup') {
           // Could dispatch a logout event here
        }
      }
    } else if (error.request) {
      // Request was made but no response
      message = 'Unable to connect to server. Please check your internet connection.';
    } else {
      // Something happened in setting up the request
      message = error.message;
    }

    // Dispatch a custom event for the UI to pick up (e.g. Toasts)
    // We'll listen for 'api-error' in our main App component or ToastProvider
    const event = new CustomEvent('api-error', { 
        detail: { message, title: error.response?.status ? `Error ${error.response.status}` : 'Error' }
    });
    window.dispatchEvent(event);

    return Promise.reject(error);
  }
);
