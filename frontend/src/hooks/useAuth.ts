import { createContext, createElement, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import i18n from '@/lib/i18n';
import { loginUser, fetchCurrentUser } from '@/services/api';
import { AUTH_CHANGED_EVENT, TOKEN_STORAGE_KEY, setAuthTokens, getAccessToken, clearAccessToken, isApiError } from '@/api/client';
import type { BackendUser } from '@/api/types';

interface AuthContextValue {
  user: BackendUser | null;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string, role: string) => Promise<BackendUser | null>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<BackendUser | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(() => !!getAccessToken());
  const [error, setError] = useState<string | null>(null);

  const refreshUser = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
        setIsLoading(false);
        return;
    }
    setIsLoading(true);
    try {
      const data = await fetchCurrentUser();
      setUser(data);
      setError(null);
    } catch (err: unknown) {
      if (isApiError(err) && (err.status === 401 || err.status === 403)) {
        clearAccessToken();
        setUser(null);
        return;
      }
      setError(err instanceof Error ? err.message : i18n.t('auth.errors.refreshFailed'));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  // Keep auth state consistent across refresh failures and multi-tab changes.
  useEffect(() => {
    const onAuthChanged = (evt: Event) => {
      const detail = (evt as CustomEvent<any>).detail;
      const token = detail?.token as string | null | undefined;
      if (!token) {
        setUser(null);
      } else {
        refreshUser();
      }
    };

    const onStorage = (evt: StorageEvent) => {
      if (evt.key !== TOKEN_STORAGE_KEY) return;
      if (!evt.newValue) {
        setUser(null);
      } else {
        refreshUser();
      }
    };

    window.addEventListener(AUTH_CHANGED_EVENT, onAuthChanged as EventListener);
    window.addEventListener('storage', onStorage);
    return () => {
      window.removeEventListener(AUTH_CHANGED_EVENT, onAuthChanged as EventListener);
      window.removeEventListener('storage', onStorage);
    };
  }, [refreshUser]);

  const login = useCallback(async (email: string, password: string, role: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const token = await loginUser({ email, password, role });
      setAuthTokens({ accessToken: token.access_token, refreshToken: token.refresh_token ?? null });
      const data = await fetchCurrentUser();
      setUser(data);
      return data;
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : i18n.t('auth.errors.loginFailed'));
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    clearAccessToken();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, isLoading, error, login, logout, refreshUser }),
    [user, isLoading, error, login, logout, refreshUser]
  );

  return createElement(AuthContext.Provider, { value }, children);
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
