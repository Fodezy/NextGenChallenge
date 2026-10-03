import { useCallback, useEffect, useState } from 'react';
import { ApiError } from './api';

export type AsyncState<T> =
  | { status: 'loading' }
  | { status: 'error'; error: ApiError }
  | { status: 'ok'; data: T };

/** Runs `load` whenever `deps` change (aborting the previous run); `reload` runs it again. */
export function useAsync<T>(
  load: (signal: AbortSignal) => Promise<T>,
  deps: readonly unknown[],
): AsyncState<T> & { reload: () => void } {
  const [state, setState] = useState<AsyncState<T>>({ status: 'loading' });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const ctrl = new AbortController();
    setState({ status: 'loading' });
    load(ctrl.signal)
      .then((data) => {
        if (!ctrl.signal.aborted) setState({ status: 'ok', data });
      })
      .catch((err: unknown) => {
        if (ctrl.signal.aborted) return;
        const error =
          err instanceof ApiError ? err : new ApiError(0, 'unexpected', 'Something went wrong');
        setState({ status: 'error', error });
      });
    return () => ctrl.abort();
  }, [...deps, attempt]); // `load` is re-created every render; the caller's deps decide reruns

  const reload = useCallback(() => setAttempt((n) => n + 1), []);
  return { ...state, reload };
}
