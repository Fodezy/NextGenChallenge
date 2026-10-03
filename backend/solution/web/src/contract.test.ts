import { describe, expect, it } from 'vitest';
import { checkContract } from './api';
import { AllocationSchema, HoldingsSchema, PortfolioSchema } from './contract';
import { mockAllocation, mockHoldings } from './mocks';

describe('mocks match the contract and the BRIEF.md examples', () => {
  it('P-9001 holdings follow R3/R4', () => {
    const rows = checkContract('mock', HoldingsSchema, mockHoldings('P-9001'));
    const aapl = rows.find((h) => h.ticker === 'AAPL');
    expect(aapl).toMatchObject({ marketValue: 27300, unrealizedGainLoss: 3300, dayChangeAmount: 300 });
    expect(aapl?.weightPercent).toBeCloseTo(0.55794, 5);
    expect(rows.find((h) => h.ticker === 'ZERO')).toMatchObject({
      marketValue: 0,
      weightPercent: 0,
      unrealizedGainLoss: 0,
      dayChangeAmount: 0,
    });
  });
  it('zero previous close gives a null day change % (A2)', () => {
    expect(mockHoldings('P-9002')?.[0]?.dayChangePercent).toBeNull();
  });
  it('allocation follows R6; empty and unknown portfolios behave', () => {
    const p9001 = checkContract('mock', AllocationSchema, mockAllocation('P-9001'));
    expect(p9001.map((a) => a.assetClass)).toEqual(['Equity', 'Fixed Income']);
    expect(mockAllocation('P-SINGLE')).toEqual([{ assetClass: 'Equity', value: 2275, percent: 1 }]);
    expect(mockAllocation('P-EMPTY')).toEqual([]);
    expect(mockHoldings('P-NOPE')).toBeUndefined();
  });
});

describe('checkContract', () => {
  it('names the field that drifted from the contract', () => {
    const bad = { portfolioId: 'P-9001', stale: 'no' };
    expect(() => checkContract('/portfolios/P-9001', PortfolioSchema, bad)).toThrow(
      /\/portfolios\/P-9001: clientId/,
    );
  });
});
