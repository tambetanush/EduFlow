import axios, { AxiosError, type AxiosRequestConfig } from 'axios';
import { getStoredLanguage } from '@/lib/i18n';

export const TOKEN_STORAGE_KEY = 'eduflow_access_token';
export const REFRESH_TOKEN_STORAGE_KEY = 'eduflow_refresh_token';
export const AUTH_CHANGED_EVENT = 'eduflow:auth:changed';

const DEFAULT_API_BASE = 'http://localhost:8000';

// VITE_API_BASE_URL should be the backend origin, without /api/v1 (e.g. http://localhost:8000)
const API_BASE_URL = String(import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE).replace(/\/+$/, '');

let accessToken: string | null = null;
let refreshToken: string | null = null;
let refreshPromise: Promise<string | null> | null = null;

const safeLocalStorage = () => (typeof window !== 'undefined' ? window.localStorage : null);

const emitAuthChanged = (token: string | null) => {
  if (typeof window === 'undefined') return;
  try {
    window.dispatchEvent(new CustomEvent(AUTH_CHANGED_EVENT, { detail: { token } }));
  } catch {
    // ignore
  }
};

const storeTokens = (tokens: { accessToken?: string | null; refreshToken?: string | null }) => {
  if (tokens.accessToken !== undefined) accessToken = tokens.accessToken;
  if (tokens.refreshToken !== undefined) refreshToken = tokens.refreshToken;

  const storage = safeLocalStorage();
  if (storage) {
    if (tokens.accessToken !== undefined) {
      if (tokens.accessToken) storage.setItem(TOKEN_STORAGE_KEY, tokens.accessToken);
      else storage.removeItem(TOKEN_STORAGE_KEY);
    }
    if (tokens.refreshToken !== undefined) {
      if (tokens.refreshToken) storage.setItem(REFRESH_TOKEN_STORAGE_KEY, tokens.refreshToken);
      else storage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
    }
  }

  if (tokens.accessToken !== undefined) {
    emitAuthChanged(tokens.accessToken);
  }
};

const loadToken = () => {
  if (accessToken) return accessToken;
  const storage = safeLocalStorage();
  if (!storage) return null;
  const stored = storage.getItem(TOKEN_STORAGE_KEY);
  if (stored) accessToken = stored;
  return accessToken;
};

const loadRefreshToken = () => {
  if (refreshToken) return refreshToken;
  const storage = safeLocalStorage();
  if (!storage) return null;
  const stored = storage.getItem(REFRESH_TOKEN_STORAGE_KEY);
  if (stored) refreshToken = stored;
  return refreshToken;
};

const api = axios.create({
  baseURL: API_BASE_URL + '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Separate client to avoid interceptor loops during refresh.
const refreshClient = axios.create({
  baseURL: API_BASE_URL + '/api/v1',
  timeout: 30000,
});

const refreshAccessToken = async () => {
  const currentRefreshToken = loadRefreshToken();
  if (!currentRefreshToken) throw new Error('Missing refresh token for refreshing session.');

  const response = await refreshClient.post('/auth/refresh', {
    refresh_token: currentRefreshToken,
  });
  const tokenData = response.data as { access_token?: string; refresh_token?: string };
  const newAccessToken = tokenData.access_token;
  const newRefreshToken = tokenData.refresh_token;

  if (!newAccessToken) throw new Error('Refresh endpoint did not return an access token.');

  storeTokens({
    accessToken: newAccessToken,
    refreshToken: newRefreshToken ?? currentRefreshToken,
  });

  return newAccessToken;
};

api.interceptors.request.use((config) => {
  const token = loadToken();
  const language = getStoredLanguage();
  config.headers = config.headers ?? {};
  if (token) {
    (config.headers as Record<string, string>)['Authorization'] = 'Bearer ' + token;
  }
  (config.headers as Record<string, string>)['Accept-Language'] = language;
  return config;
});

type RefreshableRequestConfig = AxiosRequestConfig & { _retry?: boolean };

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError & { config?: RefreshableRequestConfig }) => {
    const originalRequest = error.config;

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !String(originalRequest.url || '').includes('/auth/refresh')
    ) {
      const currentRefreshToken = loadRefreshToken();
      if (!currentRefreshToken) {
        storeTokens({ accessToken: null, refreshToken: null });
        return Promise.reject(error);
      }

      originalRequest._retry = true;

      if (!refreshPromise) {
        refreshPromise = refreshAccessToken()
          .catch(() => {
            storeTokens({ accessToken: null, refreshToken: null });
            return null;
          })
          .finally(() => {
            refreshPromise = null;
          });
      }

      const token = await refreshPromise;
      if (!token) return Promise.reject(error);

      originalRequest.headers = originalRequest.headers ?? {};
      (originalRequest.headers as Record<string, string>)['Authorization'] = 'Bearer ' + token;
      return api(originalRequest);
    }

    return Promise.reject(error);
  }
);

const pickBackendMessage = (data: any): string | null => {
  if (!data) return null;
  if (typeof data === 'string') return data;
  if (typeof data?.detail === 'string') return data.detail;
  if (Array.isArray(data?.detail) && data.detail.length > 0) {
    // FastAPI validation errors
    const first = data.detail[0];
    const msg = first?.msg || first?.message;
    return typeof msg === 'string' ? msg : null;
  }
  if (typeof data?.message === 'string') return data.message;
  return null;
};

export class ApiError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export const isApiError = (error: unknown): error is ApiError =>
  error instanceof ApiError;

const handleError = (error: unknown) => {
  if (axios.isAxiosError(error)) {
    const message = pickBackendMessage(error.response?.data) || error.message;
    throw new ApiError(message || (getStoredLanguage() === 'hi' ? 'कुछ गलत हो गया।' : 'Something went wrong.'), error.response?.status);
  }
  throw error;
};

export const apiGet = async <T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T> => {
  try {
    const response = await api.get<T>(url, config);
    return response.data;
  } catch (error) {
    handleError(error);
  }
};

export const apiPost = async <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> => {
  try {
    const response = await api.post<T>(url, data, config);
    return response.data;
  } catch (error) {
    handleError(error);
  }
};

export const apiPatch = async <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> => {
  try {
    const response = await api.patch<T>(url, data, config);
    return response.data;
  } catch (error) {
    handleError(error);
  }
};

export const apiDelete = async <T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T> => {
  try {
    const response = await api.delete<T>(url, config);
    return response.data;
  } catch (error) {
    handleError(error);
  }
};

export const setAuthTokens = (tokens: { accessToken: string | null; refreshToken?: string | null }) =>
  storeTokens({ accessToken: tokens.accessToken, refreshToken: tokens.refreshToken });
export const setAccessToken = (token: string | null) => storeTokens({ accessToken: token });
export const getAccessToken = () => loadToken();
export const clearAccessToken = () => storeTokens({ accessToken: null, refreshToken: null });

export default api;



