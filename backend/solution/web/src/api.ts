// Tiny API client. All calls go through the Vite dev proxy (/api -> http://localhost:3000).

export const API_BASE = '/api';
export const DEFAULT_TOKEN = 'superday-demo-token';

/** Flat error shape from the backend: { error: "<code>", message: "<text>" }. */
export class ApiError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
  }
}

export function buildRequest(
  path: string,
  token: string = import.meta.env.VITE_API_TOKEN || DEFAULT_TOKEN,
): { url: string; headers: Record<string, string> } {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return {
    url: `${API_BASE}${cleanPath}`,
    headers: { Accept: 'application/json', Authorization: `Bearer ${token}` },
  };
}

export async function get<T>(path: string, init?: { signal?: AbortSignal }): Promise<T> {
  const { url, headers } = buildRequest(path);
  let res: Response;
  try {
    res = await fetch(url, { headers, signal: init?.signal });
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') throw err;
    throw new ApiError(0, 'network_error', 'Cannot reach the API');
  }
  const body: unknown = await res.json().catch(() => null);
  if (!res.ok) {
    const e = (body ?? {}) as { error?: unknown; message?: unknown };
    throw new ApiError(
      res.status,
      typeof e.error === 'string' ? e.error : 'http_error',
      typeof e.message === 'string' ? e.message : `HTTP ${res.status}`,
    );
  }
  return body as T;
}
