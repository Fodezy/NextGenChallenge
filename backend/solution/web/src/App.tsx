import { useState } from 'react';
import { getPortfolio } from './api';
import type { Portfolio } from './contract';
import { Skeleton } from './components/ui';
import { Allocation } from './sections/Allocation';
import { Holdings } from './sections/Holdings';
import { Performance } from './sections/Performance';
import { Summary } from './sections/Summary';
import { useAsync, type AsyncState } from './useAsync';

// Hard-coded until GET /clients/:id/portfolios exists (Task 6, a Could).
const PORTFOLIOS = [
  { id: 'P-9001', label: 'Taxable Brokerage' },
  { id: 'P-9002', label: 'Retirement Account' },
  { id: 'P-EMPTY', label: 'Empty Account' },
] as const;

export default function App() {
  const [portfolioId, setPortfolioId] = useState<string>(PORTFOLIOS[0].id);
  const portfolio = useAsync((signal) => getPortfolio(portfolioId, signal), [portfolioId]);

  return (
    <div className="min-h-screen bg-ground text-ink">
      <main className="mx-auto flex max-w-[1200px] flex-col gap-5 px-4 pt-6 pb-10 sm:px-8">
        <header className="flex flex-wrap items-center justify-between gap-3">
          <ClientHeading state={portfolio} />
          <div className="flex items-center gap-2">
            <label htmlFor="portfolio" className="text-[13px] text-muted">
              Portfolio
            </label>
            <select
              id="portfolio"
              value={portfolioId}
              onChange={(e) => setPortfolioId(e.target.value)}
              className="min-h-10 rounded-lg border border-control bg-white px-3 text-sm text-ink focus-visible:outline-2 focus-visible:outline-accent"
            >
              {PORTFOLIOS.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.label} · {p.id}
                </option>
              ))}
            </select>
          </div>
        </header>

        <Summary state={portfolio} onRetry={portfolio.reload} />

        <div className="grid grid-cols-1 gap-5 min-[861px]:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
          <Performance portfolioId={portfolioId} />
          <Allocation portfolioId={portfolioId} />
        </div>

        <Holdings portfolioId={portfolioId} />
      </main>
    </div>
  );
}

function ClientHeading({ state }: { state: AsyncState<Portfolio> }) {
  const p = state.status === 'ok' ? state.data : null;
  return (
    <div className="flex items-center gap-2.5">
      <div aria-hidden="true" className="size-2.5 rounded-full bg-accent" />
      <div className="flex flex-col gap-0.5">
        <div className="text-[13px] font-medium text-muted">Portfolio dashboard</div>
        {state.status === 'loading' ? (
          <Skeleton className="h-8 w-48" />
        ) : (
          <h1 className="flex items-baseline gap-2.5">
            <span className="text-[28px] leading-[1.15] font-semibold tracking-[-0.4px]">
              {p?.clientName ?? 'Client'}
            </span>
            {p?.clientId && <span className="text-[13px] font-normal text-muted">Client {p.clientId}</span>}
          </h1>
        )}
      </div>
    </div>
  );
}
