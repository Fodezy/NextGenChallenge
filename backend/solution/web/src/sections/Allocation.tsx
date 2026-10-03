// Allocation by asset class from GET /portfolios/:id/allocation (Task 5; mock until it ships).
import { useState } from 'react';
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import { getAllocation } from '../api';
import type { AllocationEntry } from '../contract';
import { money, percent } from '../format';
import { Segmented } from '../components/Segmented';
import { BlockSkeleton, CardError, EmptyState } from '../components/States';
import { Card } from '../components/ui';
import { useAsync } from '../useAsync';

// Distinct in lightness, not just hue, so neighbours stay apart for colour-blind viewers.
const COLOURS = ['#0F6E6E', '#9CC9C9', '#B4690E', '#3D4652', '#E7B008'];
const VIEWS = ['Bar', 'Pie'] as const;

export function Allocation({ portfolioId }: { portfolioId: string }) {
  const [view, setView] = useState<(typeof VIEWS)[number]>('Bar');
  const allocation = useAsync((signal) => getAllocation(portfolioId, signal), [portfolioId]);

  return (
    <Card className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="m-0 text-[15px] font-semibold">Allocation</h2>
        <Segmented label="Allocation view" options={VIEWS} value={view} onChange={setView} />
      </div>
      {allocation.status === 'loading' && <BlockSkeleton label="allocation" className="h-32 w-full" />}
      {allocation.status === 'error' && (
        <CardError what="allocation" error={allocation.error} onRetry={allocation.reload} />
      )}
      {allocation.status === 'ok' &&
        (allocation.data.length === 0 ? (
          <EmptyState title="Nothing to allocate" body="This portfolio holds no positions." />
        ) : (
          <>
            {view === 'Bar' ? <Bar entries={allocation.data} /> : <PieView entries={allocation.data} />}
            <Legend entries={allocation.data} />
          </>
        ))}
    </Card>
  );
}

const describe = (entries: AllocationEntry[]) =>
  entries.map((e) => `${e.assetClass} ${percent(e.percent)}`).join(', ');

function Bar({ entries }: { entries: AllocationEntry[] }) {
  return (
    <div role="img" aria-label={describe(entries)} className="flex h-3.5 overflow-hidden rounded-full bg-ground">
      {entries.map((e, i) => (
        <div key={e.assetClass} style={{ width: `${e.percent * 100}%`, background: COLOURS[i % COLOURS.length] }} />
      ))}
    </div>
  );
}

function PieView({ entries }: { entries: AllocationEntry[] }) {
  return (
    <div role="img" aria-label={describe(entries)} className="h-48 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={entries}
            dataKey="value"
            nameKey="assetClass"
            innerRadius="55%"
            outerRadius="90%"
            stroke="#FFFFFF"
            isAnimationActive={false}
          >
            {entries.map((e, i) => (
              <Cell key={e.assetClass} fill={COLOURS[i % COLOURS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(v, name) => [money(Number(v)), String(name)]} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

function Legend({ entries }: { entries: AllocationEntry[] }) {
  return (
    <ul className="m-0 flex list-none flex-col gap-3 p-0 text-sm">
      {entries.map((e, i) => (
        <li key={e.assetClass} className="grid grid-cols-[12px_minmax(0,1fr)_auto_auto] items-center gap-2.5">
          <span aria-hidden="true" className="size-3 rounded-[3px]" style={{ background: COLOURS[i % COLOURS.length] }} />
          <span>{e.assetClass}</span>
          <span className="num">{money(e.value)}</span>
          <span className="num min-w-14 text-right text-muted">{percent(e.percent)}</span>
        </li>
      ))}
    </ul>
  );
}
