import { useEffect, useState } from 'react';
import { ApiError, get } from './api';

type Health = { status: string };
type State =
  | { kind: 'loading' }
  | { kind: 'ok'; status: string }
  | { kind: 'error'; message: string };

export default function App() {
  const [state, setState] = useState<State>({ kind: 'loading' });

  useEffect(() => {
    const ctrl = new AbortController();
    get<Health>('/health', { signal: ctrl.signal })
      .then((h) => setState({ kind: 'ok', status: h.status }))
      .catch((err: unknown) => {
        if (ctrl.signal.aborted) return;
        const message =
          err instanceof ApiError ? `${err.code}: ${err.message}` : 'Unexpected error';
        setState({ kind: 'error', message });
      });
    return () => ctrl.abort();
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 p-6 text-slate-900">
      <h1 className="text-xl font-semibold">Portfolio Dashboard</h1>
      <p className="mt-4" role="status">
        {state.kind === 'loading' && <span className="text-slate-500">API: checking…</span>}
        {state.kind === 'ok' && <span className="text-emerald-700">API: {state.status}</span>}
        {state.kind === 'error' && (
          <span className="text-red-700">
            API unavailable ({state.message}). Is uvicorn running on :3000?
          </span>
        )}
      </p>
    </main>
  );
}
