import { describe, expect, it } from 'vitest';
import { checkContract } from './api';
import { AllocationSchema, HoldingsSchema, PortfolioSchema } from './contract';

// Samples copied from the live API (P-9001 and P-9002), so the schemas stay in step with it.
const HOLDINGS_P9002 = [
  {
    ticker: 'NEW', name: 'New Security', assetClass: 'Equity', quantity: 10, costBasisPerShare: 40,
    price: 50, previousClosePrice: 0, marketValue: 500, weightPercent: 1, unrealizedGainLoss: 100,
    dayChangeAmount: 500, dayChangePercent: null,
  },
];
const ALLOCATION_P9001 = [
  { assetClass: 'Equity', value: 27300, percent: 0.5579399141630901 },
  { assetClass: 'Fixed Income', value: 21630, percent: 0.44206008583690987 },
];

describe('contract schemas accept live responses', () => {
  it('holdings with a null day change % (zero previous close, A2)', () => {
    expect(checkContract('/holdings', HoldingsSchema, HOLDINGS_P9002)[0]?.dayChangePercent).toBeNull();
  });
  it('allocation, and an empty portfolio', () => {
    expect(checkContract('/allocation', AllocationSchema, ALLOCATION_P9001)).toHaveLength(2);
    expect(checkContract('/allocation', AllocationSchema, [])).toEqual([]);
  });
});

describe('checkContract', () => {
  it('names the field that drifted from the contract', () => {
    const bad = { portfolioId: 'P-9001', stale: 'no' };
    expect(() => checkContract('/portfolios/P-9001', PortfolioSchema, bad)).toThrow(
      /\/portfolios\/P-9001: clientId/,
    );
  });
  it('rejects a percent sent as a string', () => {
    const bad = [{ assetClass: 'Equity', value: 500, percent: '100%' }];
    expect(() => checkContract('/allocation', AllocationSchema, bad)).toThrow(/0\.percent/);
  });
});
