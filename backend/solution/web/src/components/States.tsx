import type { ReactNode } from 'react';
import type { ApiError } from '../api';
import { ErrorIcon, Skeleton } from './ui';

/** Dashed empty-state box (no history, no holdings, nothing to allocate). */
export function EmptyState({ title, body, children }: { title: string; body: string; children?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center gap-1.5 rounded-lg border border-dashed border-control px-4 py-8 text-center">
      <div className="text-[15px] font-semibold">{title}</div>
      <div className="text-[13px] text-muted">{body}</div>
      {children}
    </div>
  );
}

/** Inline error for one card; the rest of the page keeps working. */
export function CardError({ what, error, onRetry }: { what: string; error: ApiError; onRetry: () => void }) {
  const body =
    error.code === 'network_error'
      ? 'Check that the backend is running on port 3000.'
      : error.code === 'not_found'
        ? 'This portfolio was not found.'
        : error.message;
  return (
    <div role="alert" className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-error-line px-4 py-4">
      <div className="flex items-start gap-3">
        <ErrorIcon />
        <div className="flex flex-col gap-0.5">
          <div className="text-sm font-semibold">Couldn't load {what}</div>
          <div className="text-[13px] text-muted">{body}</div>
        </div>
      </div>
      <button
        type="button"
        onClick={onRetry}
        className="min-h-10 cursor-pointer rounded-lg border border-control bg-white px-4 text-sm font-medium hover:bg-ground focus-visible:outline-2 focus-visible:outline-accent"
      >
        Try again
      </button>
    </div>
  );
}

export function BlockSkeleton({ label, className }: { label: string; className: string }) {
  return (
    <div aria-busy="true">
      <Skeleton className={className} />
      <span className="sr-only" role="status">
        Loading {label}…
      </span>
    </div>
  );
}
