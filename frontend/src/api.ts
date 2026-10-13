/* ============================================================
   API Client — LOTM Tarot Frontend
   Single source of truth for all backend communication.
   Components never call fetch directly.
   ============================================================ */

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '';

// --- Shared Types (mirror backend Pydantic schemas) ---

export interface APIError {
  error: {
    code: string;
    message: string;
    request_id: string | null;
    details: unknown[];
  };
}

export interface UserRead {
  id: string;
  username: string;
  email: string;
  display_name: string;
  email_verified: boolean;
  created_at: string;
  last_login: string | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: 'bearer';
  expires_in: number;
  user: UserRead;
}

export interface TarotCardSummary {
  id: number;
  name: string;
  arcana_type: string;
  card_number: number;
  upright_meaning: string;
  reversed_meaning: string;
  mystical_lore: string | null;
  image_asset_path: string | null;
}

export interface ReadingCard {
  id: string;
  card_id: number;
  position_index: number;
  position_name: string;
  is_reversed: boolean;
  card_notes: string | null;
  card: TarotCardSummary | null;
}

export type SpreadType = 'single_card' | 'three_card' | 'celtic_cross';

export interface ReadingRead {
  id: string;
  user_id: string | null;
  spread_type: SpreadType;
  question: string | null;
  interpretation: string | null;
  is_favorite: boolean;
  created_at: string;
  cards: ReadingCard[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// --- Token storage (in-memory only — never localStorage for auth tokens) ---
let _accessToken: string | null = null;

export const auth = {
  setToken: (token: string) => { _accessToken = token; },
  clearToken: () => { _accessToken = null; },
  getToken: () => _accessToken,
};

// --- HTTP client core ---
class APIRequestError extends Error {
  readonly status: number;
  readonly body: APIError;
  constructor(status: number, body: APIError) {
    super(body.error.message);
    this.name = 'APIRequestError';
    this.status = status;
    this.body = body;
  }
}
export { APIRequestError };

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> ?? {}),
  };

  if (_accessToken) {
    headers['Authorization'] = `Bearer ${_accessToken}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const body: APIError = await res.json().catch(() => ({
      error: { code: 'UNKNOWN_ERROR', message: res.statusText, request_id: null, details: [] },
    }));
    throw new APIRequestError(res.status, body);
  }

  if (res.status === 204) return undefined as unknown as T;
  return res.json() as Promise<T>;
}

// --- Auth endpoints ---
export const authApi = {
  register: (data: { username: string; email: string; display_name: string; password: string }) =>
    request<TokenResponse>('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  login: (data: { username_or_email: string; password: string }) =>
    request<TokenResponse>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  me: () => request<UserRead>('/api/v1/auth/me'),
};

// --- Readings endpoints ---
export const readingsApi = {
  create: (data: { spread_type: SpreadType; question?: string }) =>
    request<ReadingRead>('/api/v1/readings', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  list: (params?: { page?: number; page_size?: number; is_favorite?: boolean }) => {
    const q = new URLSearchParams();
    if (params?.page)        q.set('page', String(params.page));
    if (params?.page_size)   q.set('page_size', String(params.page_size));
    if (params?.is_favorite !== undefined) q.set('is_favorite', String(params.is_favorite));
    return request<PaginatedResponse<ReadingRead>>(`/api/v1/readings?${q.toString()}`);
  },

  get: (id: string) => request<ReadingRead>(`/api/v1/readings/${id}`),

  toggleFavorite: (id: string, is_favorite: boolean) =>
    request<ReadingRead>(`/api/v1/readings/${id}/favorite`, {
      method: 'PATCH',
      body: JSON.stringify({ is_favorite }),
    }),
};
