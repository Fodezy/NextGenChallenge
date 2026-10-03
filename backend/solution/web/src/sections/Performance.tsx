// Performance line chart from GET /portfolios/:id/performance-history (Task 3).
import { useState } from 'react';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { getHistory } from '../api';
import { RANGES, type HistoryPoint, type Range } from '../contract';
import { dayLabel, money } from '../format';
import { Segmented } from '../components/Segmented';
import { BlockSkeleton, CardError, EmptyState } from '../components/States';
import { Card } from '../components/ui';
import { useAsync } from '../useAsync';

const compact = new Intl.NumberFormat('en-CA', {
  style: 'currency',
  currency: 'CAD',
  notation: 'compact',
  maximumFractionDigits: 1,
});

export function Performance({ portfolioId }: { portfolioId: string }) {
  const [range, setRange] = useState<Range>('All');
  const history = useAsync((signal) => getHistory(portfolioId, range, signal), [portfolioId, range]);

  return (
    <Card className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="m-0 text-[15px] font-semibold">Performance</h2>
        <Segmented label="Range" options={RANGES} value={range} onChange={setRange} />
      </div>
      {history.status === 'loading' && <BlockSkeleton label="performance" className="h-[240px] w-full" />}
      {history.status === 'error' && (
        <CardError what="performance" error={history.error} onRetry={history.reload} />
      )}
      {history.status === 'ok' &&
        (history.data.length === 0 ? (
          <EmptyState
            title={range === 'All' ? 'No history yet' : 'No history in this range'}
            body={
              range === 'All'
                ? "The chart fills in after this portfolio's first daily value."
                : 'Try a longer range.'
            }
          />
        ) : (
          <>
            <Chart points={history.data} />
            <ShortHistoryNote points={history.data} range={range} />
          </>
        ))}
    </Card>
  );
}

function Chart({ points }: { points: HistoryPoint[] }) {
  const first = points[0];
  const last = points[points.length - 1];
  const summary =
    first && last
      ? `Market value from ${money(first.marketValue)} on ${dayLabel(first.date)} to ${money(last.marketValue)} on ${dayLabel(last.date)}`
      : 'Market value';
  return (
    <div role="img" aria-label={summary} className="h-[240px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={points} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
          <CartesianGrid stroke="#EEF0F2" vertical={false} />
          <XAxis
            dataKey="date"
            tickFormatter={dayLabel}
            minTickGap={48}
            tick={{ fontSize: 11, fill: '#5B6470' }}
            tickLine={false}
            axisLine={{ stroke: '#E3E6EA' }}
          />
          <YAxis
            domain={['auto', 'auto']}
            tickFormatter={(v: number) => compact.format(v)}
            width={64}
            tick={{ fontSize: 11, fill: '#5B6470', fontFamily: 'IBM Plex Mono, monospace' }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            formatter={(v) => [money(Number(v)), 'Market value']}
            labelFormatter={(d) => dayLabel(String(d))}
            contentStyle={{ borderRadius: 8, borderColor: '#E3E6EA', fontSize: 13 }}
          />
          <Area
            type="monotone"
            dataKey="marketValue"
            stroke="#0F6E6E"
            strokeWidth={2}
            fill="#0F6E6E"
            fillOpacity={0.08}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

/** "Only 60 days of history" when the data starts after the range would (BRIEF.md R5, A11). */
function ShortHistoryNote({ points, range }: { points: HistoryPoint[]; range: Range }) {
  const first = points[0];
  const last = points[points.length - 1];
  if (!first || !last || range === 'All' || range === '1D') return null;
  const start = rangeStart(range, new Date());
  if (first.date <= start) return null;
  return (
    <div className="text-[13px] text-muted">
      Only {points.length} days of history so far, so {range} shows everything available (
      {dayLabel(first.date)} to {dayLabel(last.date)}).
    </div>
  );
}

function rangeStart(range: Exclude<Range, 'All' | '1D'>, now: Date): string {
  const y = now.getUTCFullYear();
  const m = now.getUTCMonth();
  const d = now.getUTCDate();
  if (range === 'YTD') return `${y}-01-01`;
  const back = range === '1M' ? 1 : 12;
  const target = new Date(Date.UTC(y, m - back, 1));
  const lastDay = new Date(Date.UTC(target.getUTCFullYear(), target.getUTCMonth() + 1, 0)).getUTCDate();
  target.setUTCDate(Math.min(d, lastDay));
  return target.toISOString().slice(0, 10);
}
