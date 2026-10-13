import { createContext } from 'react';
import type { UserRead } from '../api';

export interface AuthState {
  user: UserRead | null;
  isLoading: boolean;
}

export interface AuthContextValue extends AuthState {
  login: (usernameOrEmail: string, password: string) => Promise<void>;
  register: (username: string, email: string, displayName: string, password: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);
