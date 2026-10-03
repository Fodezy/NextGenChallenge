import type { ReactNode } from 'react';
import { tone } from '../format';

export const TONE_CLASS = { gain: 'text-gain', loss: 'text-loss', flat: 'text-muted' } as const;

export function toneClass(value: number | null | undefined): string {
  return TONE_CLASS[tone(value)];
}

export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <section className={`rounded-[10px] border border-line bg-white px-6 py-5 ${className}`}>
      {children}
    </section>
  );
}

export function Skeleton({ className }: { className: string }) {
  return <div aria-hidden="true" className={`rounded bg-skeleton ${className}`} />;
}

export function PrimaryButton({ children, onClick }: { children: ReactNode; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="min-h-11 cursor-pointer rounded-lg bg-accent px-5 text-sm font-semibold text-white hover:bg-[#0b5454] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
    >
      {children}
    </button>
  );
}

export function ErrorIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 22 22" aria-hidden="true" className="mt-0.5 flex-none text-loss">
      <circle cx="11" cy="11" r="9" fill="none" stroke="currentColor" strokeWidth="1.6" />
      <path d="M11 6.5 V12" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <circle cx="11" cy="15.5" r="1.1" fill="currentColor" />
    </svg>
  );
}

export function ClockIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true" className="mt-px flex-none">
      <circle cx="10" cy="10" r="8" fill="none" stroke="currentColor" strokeWidth="1.6" />
      <path d="M10 5.5 V10.5 L13 12.5" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}
