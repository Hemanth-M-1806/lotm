import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { Nav } from './components/Nav';
import { OraclePage } from './pages/OraclePage';
import { LoginPage } from './pages/LoginPage';
import { HistoryPage } from './pages/HistoryPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Nav />
          <Routes>
            <Route path="/" element={<OraclePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

function NotFound() {
  return (
    <main style={{ minHeight: '100dvh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div className="empty-state">
        <div className="empty-state__sigil" aria-hidden="true">?</div>
        <h1 className="empty-state__title">Lost in the Fog</h1>
        <p className="empty-state__body">This passage does not exist in Backlund's streets.</p>
        <a href="/" className="btn btn--ghost" style={{ marginTop: 'var(--space-6)', display: 'inline-flex' }}>
          Return to the Oracle
        </a>
      </div>
    </main>
  );
}
