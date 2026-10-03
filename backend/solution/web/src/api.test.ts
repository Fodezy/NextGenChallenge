import { afterEach, describe, expect, it, vi } from 'vitest';
import { ApiError, buildRequest, get } from './api';

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('buildRequest', () => {
  it('prefixes /api and sends the bearer token', () => {
    const { url, headers } = buildRequest('/health', 'abc');
    expect(url).toBe('/api/health');
    expect(headers.Authorization).toBe('Bearer abc');
  });

  it('adds a missing leading slash and defaults the token', () => {
    const { url, headers } = buildRequest('portfolios/P-9001');
    expect(url).toBe('/api/portfolios/P-9001');
    expect(headers.Authorization).toBe('Bearer superday-demo-token');
  });
});

describe('get', () => {
  it('throws ApiError with the flat error shape', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () =>
        Response.json({ error: 'not_found', message: 'Route not found' }, { status: 404 }),
      ),
    );
    await expect(get('/nope')).rejects.toMatchObject({
      status: 404,
      code: 'not_found',
      message: 'Route not found',
    });
    await expect(get('/nope')).rejects.toBeInstanceOf(ApiError);
  });
});
