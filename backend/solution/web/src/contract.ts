// Response shapes from BRIEF.md §7. Every response is checked against these when it arrives, so a
// backend that drifts from the contract fails loudly with the field name, not as a blank screen.
import { z } from 'zod';

const money = z.number();
const maybeNumber = z.number().nullable();

export const PortfolioSchema = z.object({
  portfolioId: z.string(),
  clientId: z.string().nullable(),
  clientName: z.string().nullable(),
  label: z.string().nullable(),
  currency: z.string().nullable(),
  totalMarketValue: maybeNumber,
  dayChangeAmount: maybeNumber,
  dayChangePercent: maybeNumber,
  totalReturnSinceInception: maybeNumber,
  asOf: z.string().nullable(),
  stale: z.boolean(),
  cachedAt: z.string(),
});

export const HistorySchema = z.array(z.object({ date: z.string(), marketValue: money }));

export const HoldingSchema = z.object({
  ticker: z.string(),
  name: z.string(),
  assetClass: z.string(),
  quantity: z.number(),
  costBasisPerShare: money,
  price: money,
  previousClosePrice: money,
  marketValue: money,
  weightPercent: z.number(),
  unrealizedGainLoss: money,
  dayChangeAmount: money,
  dayChangePercent: maybeNumber,
});
export const HoldingsSchema = z.array(HoldingSchema);

export const AllocationSchema = z.array(
  z.object({ assetClass: z.string(), value: money, percent: z.number() }),
);

export type Portfolio = z.infer<typeof PortfolioSchema>;
export type HistoryPoint = z.infer<typeof HistorySchema>[number];
export type Holding = z.infer<typeof HoldingSchema>;
export type AllocationEntry = z.infer<typeof AllocationSchema>[number];

export const RANGES = ['1D', '1M', 'YTD', '1Y', 'All'] as const;
export type Range = (typeof RANGES)[number];
