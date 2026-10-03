// Stand-in for allocation (Task 5, partner B) until it ships. Holdings (Task 2) is live; its mock
// stays only because mockAllocation is built from it. Values follow BRIEF.md rules R3, R4 and R6
// applied to backend/fixtures/seed.json, so switching to the real API should change nothing on
// screen. Delete this file when allocation is live.
import type { AllocationEntry, Holding } from './contract';

type SeedHolding = Pick<
  Holding,
  'ticker' | 'name' | 'assetClass' | 'quantity' | 'costBasisPerShare' | 'price' | 'previousClosePrice'
>;

const SEED: Record<string, SeedHolding[]> = {
  'P-9001': [
    { ticker: 'AAPL', name: 'Apple Inc.', assetClass: 'Equity', quantity: 120, costBasisPerShare: 200, price: 227.5, previousClosePrice: 225 },
    { ticker: 'BND', name: 'Vanguard Total Bond ETF', assetClass: 'Fixed Income', quantity: 300, costBasisPerShare: 74, price: 72.1, previousClosePrice: 73 },
    { ticker: 'ZERO', name: 'Closed Position', assetClass: 'Equity', quantity: 0, costBasisPerShare: 10, price: 12, previousClosePrice: 10 },
  ],
  'P-9002': [
    { ticker: 'NEW', name: 'New Security', assetClass: 'Equity', quantity: 10, costBasisPerShare: 40, price: 50, previousClosePrice: 0 },
  ],
  'P-EMPTY': [],
  'P-SINGLE': [
    { ticker: 'AAPL', name: 'Apple Inc.', assetClass: 'Equity', quantity: 10, costBasisPerShare: 200, price: 227.5, previousClosePrice: 225 },
  ],
};

const cents = (n: number) => Math.round(n * 100) / 100;

export function mockHoldings(portfolioId: string): Holding[] | undefined {
  const rows = SEED[portfolioId];
  if (!rows) return undefined;
  const total = rows.reduce((sum, h) => sum + h.quantity * h.price, 0);
  return rows.map((h) => {
    const marketValue = h.quantity * h.price;
    return {
      ...h,
      marketValue: cents(marketValue),
      weightPercent: total === 0 ? 0 : marketValue / total,
      unrealizedGainLoss: cents((h.price - h.costBasisPerShare) * h.quantity),
      dayChangeAmount: cents((h.price - h.previousClosePrice) * h.quantity),
      dayChangePercent:
        h.previousClosePrice === 0 ? null : (h.price - h.previousClosePrice) / h.previousClosePrice,
    };
  });
}

export function mockAllocation(portfolioId: string): AllocationEntry[] | undefined {
  const holdings = mockHoldings(portfolioId);
  if (!holdings) return undefined;
  const total = holdings.reduce((sum, h) => sum + h.marketValue, 0);
  const byClass = new Map<string, number>();
  for (const h of holdings) byClass.set(h.assetClass, (byClass.get(h.assetClass) ?? 0) + h.marketValue);
  return [...byClass].map(([assetClass, value]) => ({
    assetClass,
    value: cents(value),
    percent: total === 0 ? 0 : value / total,
  }));
}
