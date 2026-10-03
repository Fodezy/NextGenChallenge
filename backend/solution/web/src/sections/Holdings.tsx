// Holdings table from GET /portfolios/:id/holdings (Task 2).
// Filters are client-side on the loaded rows; weights stay relative to the whole portfolio.
import { useMemo, useState } from 'react';
import { getHoldings } from '../api';
import type { Holding } from '../contract';
import { NONE, money, percent, quantity } from '../format';
import { Segmented } from '../components/Segmented';
import { BlockSkeleton, CardError, EmptyState } from '../components/States';
import { Card, toneClass } from '../components/ui';
import { useAsync } from '../useAsync';

const ALL = 'All';

export function Holdings({ portfolioId }: { portfolioId: string }) {
  const holdings = useAsync((signal) => getHoldings(portfolioId, signal), [portfolioId]);

  return (
    <Card className="flex flex-col gap-3">
      {holdings.status === 'loading' && (
        <>
          <h2 className="m-0 text-[15px] font-semibold">Holdings</h2>
          <BlockSkeleton label="holdings" className="h-40 w-full" />
        </>
      )}
      {holdings.status === 'error' && (
        <>
          <h2 className="m-0 text-[15px] font-semibold">Holdings</h2>
          <CardError what="holdings" error={holdings.error} onRetry={holdings.reload} />
        </>
      )}
      {holdings.status === 'ok' && <HoldingsTable key={portfolioId} rows={holdings.data} />}
    </Card>
  );
}

function HoldingsTable({ rows }: { rows: Holding[] }) {
  const [query, setQuery] = useState('');
  const [assetClass, setAssetClass] = useState<string>(ALL);
  const [hideClosed, setHideClosed] = useState(false);
  const [descending, setDescending] = useState(true);

  const classes = useMemo(() => [ALL, ...new Set(rows.map((h) => h.assetClass))], [rows]);
  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return rows
      .filter((h) => !q || h.ticker.toLowerCase().includes(q) || h.name.toLowerCase().includes(q))
      .filter((h) => assetClass === ALL || h.assetClass === assetClass)
      .filter((h) => !hideClosed || h.quantity !== 0)
      .sort((a, b) => (descending ? b.marketValue - a.marketValue : a.marketValue - b.marketValue));
  }, [rows, query, assetClass, hideClosed, descending]);

  const filtered = query !== '' || assetClass !== ALL || hideClosed;
  const clear = () => {
    setQuery('');
    setAssetClass(ALL);
    setHideClosed(false);
  };

  return (
    <>
      <div className="flex items-baseline justify-between gap-3">
        <h2 className="m-0 text-[15px] font-semibold">Holdings</h2>
        <div className="text-[13px] text-muted" aria-live="polite">
          Showing {visible.length} of {rows.length} position{rows.length === 1 ? '' : 's'}
        </div>
      </div>

      {rows.length === 0 ? (
        <EmptyState title="No holdings yet" body="Positions appear here once this portfolio buys something." />
      ) : (
        <>
          <div className="flex flex-col gap-2.5">
            <div className="relative w-full max-w-[360px]">
              <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true" className="absolute top-3 left-3 text-muted">
                <circle cx="7" cy="7" r="5" fill="none" stroke="currentColor" strokeWidth="1.5" />
                <path d="M11 11 L14 14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
              <input
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                aria-label="Filter holdings by ticker or name"
                placeholder="Filter by ticker or name"
                className="min-h-10 w-full rounded-lg border border-control bg-white pr-3 pl-9 text-sm focus-visible:outline-2 focus-visible:outline-accent"
              />
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <Segmented label="Asset class" options={classes} value={assetClass} onChange={setAssetClass} />
              <label className="inline-flex min-h-10 cursor-pointer items-center gap-2 text-[13px]">
                <input
                  type="checkbox"
                  checked={hideClosed}
                  onChange={(e) => setHideClosed(e.target.checked)}
                  className="m-0 size-4 accent-accent"
                />
                Hide closed positions
              </label>
              {filtered && (
                <button
                  type="button"
                  onClick={clear}
                  className="min-h-10 cursor-pointer px-1 text-[13px] font-medium text-accent underline-offset-2 hover:underline focus-visible:outline-2 focus-visible:outline-accent"
                >
                  Clear filters
                </button>
              )}
            </div>
          </div>

          {visible.length === 0 ? (
            <EmptyState title="No holdings match" body="Try another search or clear the filters.">
              <button
                type="button"
                onClick={clear}
                className="mt-2 min-h-10 cursor-pointer rounded-lg border border-control bg-white px-4 text-sm font-medium hover:bg-ground"
              >
                Clear filters
              </button>
            </EmptyState>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-sm">
                <thead>
                  <tr className="text-xs font-semibold whitespace-nowrap text-muted">
                    <Th left>Security</Th>
                    <Th left>Asset class</Th>
                    <Th>Quantity</Th>
                    <Th>Avg cost</Th>
                    <Th>Price</Th>
                    <th aria-sort={descending ? 'descending' : 'ascending'} className="border-b border-line px-3 py-2.5 text-right">
                      <button
                        type="button"
                        onClick={() => setDescending((d) => !d)}
                        className="inline-flex min-h-6 cursor-pointer items-center gap-1 font-semibold text-ink focus-visible:outline-2 focus-visible:outline-accent"
                      >
                        Market value
                        <svg width="10" height="10" viewBox="0 0 10 10" aria-hidden="true" className={descending ? '' : 'rotate-180'}>
                          <path d="M2 3.5 L5 6.5 L8 3.5" fill="none" stroke="currentColor" strokeWidth="1.5" />
                        </svg>
                      </button>
                    </th>
                    <Th>Weight</Th>
                    <Th>Unrealized gain/loss</Th>
                    <Th>Today</Th>
                  </tr>
                </thead>
                <tbody>
                  {visible.map((h) => (
                    <Row key={h.ticker} h={h} />
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {rows.some((h) => h.dayChangePercent === null || h.quantity === 0) && (
            <div className="text-xs text-muted">
              {NONE} No day change %: the position is closed or has no previous close to compare against.
            </div>
          )}
        </>
      )}
    </>
  );
}

function Th({ children, left = false }: { children: string; left?: boolean }) {
  return <th className={`border-b border-line px-3 py-2.5 ${left ? 'text-left' : 'text-right'}`}>{children}</th>;
}

function Row({ h }: { h: Holding }) {
  // Review decision: a closed (0-share) position shows "—" for today's %, not the price move.
  const dayPct = h.quantity === 0 ? null : h.dayChangePercent;
  return (
    <tr className="border-b border-[#EEF0F2] whitespace-nowrap">
      <td className="px-3 py-3 text-left">
        <div className="font-semibold">{h.ticker}</div>
        <div className="text-xs text-muted">{h.name}</div>
      </td>
      <td className="px-3 py-3 text-left">{h.assetClass}</td>
      <td className="num px-3 py-3 text-right">{quantity(h.quantity)}</td>
      <td className="num px-3 py-3 text-right">{money(h.costBasisPerShare)}</td>
      <td className="num px-3 py-3 text-right">{money(h.price)}</td>
      <td className="num px-3 py-3 text-right font-semibold">{money(h.marketValue)}</td>
      <td className="num px-3 py-3 text-right">{percent(h.weightPercent)}</td>
      <td className={`num px-3 py-3 text-right ${toneClass(h.unrealizedGainLoss)}`}>
        {money(h.unrealizedGainLoss, { signed: true })}
      </td>
      <td className={`num px-3 py-3 text-right ${toneClass(h.dayChangeAmount)}`}>
        {money(h.dayChangeAmount, { signed: true })} ({percent(dayPct, { signed: true })})
      </td>
    </tr>
  );
}
