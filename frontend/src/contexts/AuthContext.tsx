import { useState, useCallback, type ReactNode } from 'react';
import { auth, authApi, type TokenResponse } from '../api';
import { AuthContext, type AuthState } from './authContextDef';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({ user: null, isLoading: false });

  const applyToken = useCallback((resp: TokenResponse) => {
    auth.setToken(resp.access_token);
    setState({ user: resp.user, isLoading: false });
  }, []);

  const login = useCallback(async (usernameOrEmail: string, password: string) => {
    setState(s => ({ ...s, isLoading: true }));
    const resp = await authApi.login({ username_or_email: usernameOrEmail, password });
    applyToken(resp);
  }, [applyToken]);

  const register = useCallback(async (
    username: string, email: string, displayName: string, password: string
  ) => {
    setState(s => ({ ...s, isLoading: true }));
    const resp = await authApi.register({ username, email, display_name: displayName, password });
    applyToken(resp);
  }, [applyToken]);

  const logout = useCallback(() => {
    auth.clearToken();
    setState({ user: null, isLoading: false });
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
