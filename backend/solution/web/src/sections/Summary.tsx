// Header KPIs from GET /portfolios/:id (Tasks 1 and 9): total value, today, since inception,
// plus the stale banner (served from cache) and the CRM-down card (503, nothing cached).
import type { ReactNode } from 'react';
import type { Portfolio } from '../contract';
import { dateTimeLabel, money, percent, timeLabel } from '../format';
import { Card, ClockIcon, ErrorIcon, PrimaryButton, Skeleton, toneClass } from '../components/ui';
import type { AsyncState } from '../useAsync';

export function Summary({ state, onRetry }: { state: AsyncState<Portfolio>; onRetry: () => void }) {
  if (state.status === 'loading') return <SummarySkeleton />;
  if (state.status === 'error') return <SummaryError message={errorText(state.error.code)} onRetry={onRetry} />;

  const p = state.data;
  return (
    <div className="flex flex-col gap-2.5">
      {p.stale && <StaleBanner cachedAt={p.cachedAt} />}
      <div className="text-[13px] text-muted">
        {[p.label ?? 'Unnamed portfolio', p.portfolioId, p.currency].filter(Boolean).join(' · ')}
      </div>
      <div className="grid grid-cols-1 gap-4 min-[861px]:grid-cols-3">
        <Kpi label="Total value" note={p.stale ? `Saved ${timeLabel(p.cachedAt)} · as of ${dateTimeLabel(p.asOf)}` : `As of ${dateTimeLabel(p.asOf)}`} warn={p.stale}>
          <div className="num text-[32px] font-semibold tracking-[-0.5px]">{money(p.totalMarketValue)}</div>
        </Kpi>
        <Kpi label="Today" note="Change since yesterday's close">
          <div className={`num text-2xl font-semibold ${toneClass(p.dayChangeAmount)}`}>
            {money(p.dayChangeAmount, { signed: true })}{' '}
            <span className="text-sm">({percent(p.dayChangePercent, { signed: true })})</span>
          </div>
        </Kpi>
        <Kpi label="Since inception" note="Total return">
          <div className={`num text-2xl font-semibold ${toneClass(p.totalReturnSinceInception)}`}>
            {percent(p.totalReturnSinceInception, { signed: true })}
          </div>
        </Kpi>
      </div>
    </div>
  );
}

function Kpi({ label, note, warn = false, children }: { label: string; note: string; warn?: boolean; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-1.5 rounded-[10px] border-[1.5px] border-line-strong bg-white px-5 py-4">
      <div className="text-xs font-semibold tracking-[0.4px] text-muted uppercase">{label}</div>
      {children}
      <div className={`text-xs ${warn ? 'font-medium text-warn-ink' : 'text-muted'}`}>{note}</div>
    </div>
  );
}

function StaleBanner({ cachedAt }: { cachedAt: string }) {
  return (
    <div role="status" className="flex items-start gap-3 rounded-[10px] border border-warn-line bg-warn-bg px-[18px] py-3.5 text-sm text-warn-ink">
      <ClockIcon />
      <div className="flex flex-col gap-0.5">
        <div className="font-semibold">Showing saved data from {timeLabel(cachedAt)}</div>
        <div>We can't reach the CRM right now, so these values may be out of date. We'll refresh them once it's back.</div>
      </div>
    </div>
  );
}

function SummaryError({ message, onRetry }: { message: { title: string; body: string }; onRetry: () => void }) {
  return (
    <Card className="!border-error-line">
      <div role="alert" className="flex flex-wrap items-center justify-between gap-5">
        <div className="flex items-start gap-3.5">
          <ErrorIcon />
          <div className="flex flex-col gap-1">
            <div className="text-base font-semibold">{message.title}</div>
            <div className="text-sm text-muted">{message.body}</div>
          </div>
        </div>
        <PrimaryButton onClick={onRetry}>Try again</PrimaryButton>
      </div>
    </Card>
  );
}

function errorText(code: string): { title: string; body: string } {
  switch (code) {
    case 'crm_unavailable':
      return {
        title: 'Portfolio summary unavailable',
        body: "We couldn't reach the CRM and don't have a saved copy yet. Your holdings and charts below still load.",
      };
    case 'not_found':
      return { title: 'Portfolio not found', body: 'The CRM has no account with this id.' };
    case 'network_error':
      return { title: "Can't reach the API", body: 'Check that the backend is running on port 3000.' };
    case 'unauthorized':
      return { title: 'Not signed in', body: 'The API rejected our token. Check VITE_API_TOKEN.' };
    default:
      return { title: 'Portfolio summary unavailable', body: 'Something went wrong loading this summary.' };
  }
}

function SummarySkeleton() {
  return (
    <div className="flex flex-col gap-2.5" aria-busy="true">
      <Skeleton className="h-3.5 w-56" />
      <div className="grid grid-cols-1 gap-4 min-[861px]:grid-cols-3">
        {[0, 1, 2].map((i) => (
          <div key={i} className="flex flex-col gap-2.5 rounded-[10px] border-[1.5px] border-line-strong bg-white px-5 py-4">
            <Skeleton className="h-3 w-24" />
            <Skeleton className="h-8 w-40" />
            <Skeleton className="h-3 w-32" />
          </div>
        ))}
      </div>
      <span className="sr-only" role="status">Loading portfolio summary…</span>
    </div>
  );
}
