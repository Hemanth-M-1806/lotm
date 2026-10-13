import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/useAuth';
import { APIRequestError } from '../api';

type FormMode = 'login' | 'register';

export function LoginPage() {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState<FormMode>('login');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form fields
  const [usernameOrEmail, setUsernameOrEmail] = useState('');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      if (mode === 'login') {
        await login(usernameOrEmail, password);
      } else {
        await register(username, email, displayName, password);
      }
      navigate('/');
    } catch (err) {
      if (err instanceof APIRequestError) {
        setError(err.body.error.message);
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main
      style={{
        minHeight: '100dvh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'var(--space-8) var(--space-4)',
      }}
      aria-label={mode === 'login' ? 'Sign in' : 'Create account'}
    >
      <Link to="/" className="font-display text-lg text-brass italic" style={{ marginBottom: 'var(--space-8)' }}>
        L.o.M. Tarot
      </Link>

      <div className="reading-panel" style={{ width: '100%', maxWidth: '28rem' }}>
        <h1 className="reading-panel__title">
          {mode === 'login' ? 'Enter the Fog' : 'Join the Order'}
        </h1>
        <p className="reading-panel__subtitle">
          {mode === 'login'
            ? 'Sign in to preserve your archive of consultations'
            : 'Create an account to begin your divination record'}
        </p>

        <form onSubmit={handleSubmit} noValidate>
          {mode === 'register' && (
            <>
              <div className="form-group">
                <label htmlFor="username" className="form-label">Username</label>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  required
                  minLength={3}
                  maxLength={50}
                  pattern="^[a-zA-Z0-9_-]+$"
                  placeholder="klein_moretti"
                  autoComplete="username"
                />
              </div>
              <div className="form-group">
                <label htmlFor="email" className="form-label">Email</label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                  maxLength={255}
                  placeholder="seeker@backlund.city"
                  autoComplete="email"
                />
              </div>
              <div className="form-group">
                <label htmlFor="display-name" className="form-label">Display Name</label>
                <input
                  id="display-name"
                  type="text"
                  value={displayName}
                  onChange={e => setDisplayName(e.target.value)}
                  required
                  maxLength={100}
                  placeholder="The Fool"
                  autoComplete="nickname"
                />
              </div>
            </>
          )}

          {mode === 'login' && (
            <div className="form-group">
              <label htmlFor="username-or-email" className="form-label">Username or email</label>
              <input
                id="username-or-email"
                type="text"
                value={usernameOrEmail}
                onChange={e => setUsernameOrEmail(e.target.value)}
                required
                placeholder="klein_moretti"
                autoComplete="username"
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="password" className="form-label">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              minLength={8}
              maxLength={128}
              placeholder={mode === 'register' ? 'At least 8 characters' : ''}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            />
          </div>

          {error && (
            <div className="alert alert--error" role="alert" aria-live="assertive">
              {error}
            </div>
          )}

          <button
            type="submit"
            className={`btn btn--primary${isLoading ? ' btn--loading' : ''}`}
            disabled={isLoading}
            style={{ width: '100%', marginBottom: 'var(--space-4)' }}
            aria-busy={isLoading}
          >
            {mode === 'login'
              ? (isLoading ? 'Entering...' : 'Sign in')
              : (isLoading ? 'Creating account...' : 'Create account')}
          </button>

          <div className="ornament-divider">or</div>

          <p style={{ textAlign: 'center', marginTop: 'var(--space-4)', color: 'var(--color-ink-secondary)', fontSize: 'var(--text-sm)' }}>
            {mode === 'login' ? (
              <>New seeker?{' '}
                <button type="button" onClick={() => setMode('register')} style={{ color: 'var(--color-brass)', background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'inherit', fontSize: 'inherit', textDecoration: 'underline' }}>
                  Create an account
                </button>
              </>
            ) : (
              <>Already initiated?{' '}
                <button type="button" onClick={() => setMode('login')} style={{ color: 'var(--color-brass)', background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'inherit', fontSize: 'inherit', textDecoration: 'underline' }}>
                  Sign in
                </button>
              </>
            )}
          </p>
        </form>
      </div>
    </main>
  );
}
