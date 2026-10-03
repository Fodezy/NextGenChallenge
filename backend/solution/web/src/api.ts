// API client. All calls go through the Vite dev proxy (/api -> http://127.0.0.1:3000).
// One function per BRIEF.md §7 endpoint; screens call only these, never fetch directly.
import type { ZodType } from 'zod';
import {
  AllocationSchema,
  HistorySchema,
  HoldingsSchema,
  PortfolioSchema,
  type AllocationEntry,
  type HistoryPoint,
  type Holding,
  type Portfolio,
  type Range,
} from './contract';

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

/** Checks a response against the contract; a mismatch names the field (join-up debugging). */
export function checkContract<T>(path: string, schema: ZodType<T>, body: unknown): T {
  const parsed = schema.safeParse(body);
  if (parsed.success) return parsed.data;
  const issue = parsed.error.issues[0];
  const where = issue?.path.length ? issue.path.join('.') : '(root)';
  throw new ApiError(0, 'contract_mismatch', `${path}: ${where} ${issue?.message ?? 'invalid'}`);
}

async function fetchChecked<T>(path: string, schema: ZodType<T>, signal?: AbortSignal): Promise<T> {
  return checkContract(path, schema, await get<unknown>(path, { signal }));
}

const portfolioPath = (id: string) => `/portfolios/${encodeURIComponent(id)}`;

export function getPortfolio(id: string, signal?: AbortSignal): Promise<Portfolio> {
  return fetchChecked(portfolioPath(id), PortfolioSchema, signal);
}

export function getHistory(id: string, range: Range, signal?: AbortSignal): Promise<HistoryPoint[]> {
  const path = `${portfolioPath(id)}/performance-history?range=${range}`;
  return fetchChecked(path, HistorySchema, signal);
}

export function getHoldings(id: string, signal?: AbortSignal): Promise<Holding[]> {
  return fetchChecked(`${portfolioPath(id)}/holdings`, HoldingsSchema, signal);
}

export function getAllocation(id: string, signal?: AbortSignal): Promise<AllocationEntry[]> {
  return fetchChecked(`${portfolioPath(id)}/allocation`, AllocationSchema, signal);
}
