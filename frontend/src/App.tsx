import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { ChatView } from './components/chat/ChatView';
import { ApprovalsPanel } from './components/approvals/ApprovalsPanel';
import { TracesPanel } from './components/traces/TracesPanel';
import { AnalyticsDashboard } from './components/analytics/AnalyticsDashboard';
import { VisualsPanel } from './components/visuals/VisualsPanel';
import { LoginPage } from './pages/LoginPage';
import { SignupPage } from './pages/SignupPage';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';
import { ResetPasswordPage } from './pages/ResetPasswordPage';
import { CompleteOAuthPage } from './pages/CompleteOAuthPage';

import { ToastProvider } from './components/ui/Toasts';
import { AuthProvider, useAuth } from './context/AuthContext';



function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <div className="flex items-center justify-center h-screen bg-gray-950 text-white">Loading...</div>;
  }
  
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />
            <Route path="/complete-oauth" element={<CompleteOAuthPage />} />
            
            <Route element={
              <ProtectedRoute>
                <AppShell />
              </ProtectedRoute>
            }>
              <Route path="/" element={<ChatView />} />
              <Route path="/c/:conversationId" element={<ChatView />} />
              <Route path="/approvals" element={<ApprovalsPanel />} />
              <Route path="/traces" element={<TracesPanel />} />
              <Route path="/analytics" element={<AnalyticsDashboard />} />
              <Route path="/visuals" element={<VisualsPanel />} />
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}


export default App;
