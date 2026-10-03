// The one format helper (CLAUDE.md): en-CA, CAD, "+" on gains, "−" (U+2212) on losses,
// "—" for values the API sends as null.

export const NONE = '—';
const MINUS = '−';

const cad = new Intl.NumberFormat('en-CA', { style: 'currency', currency: 'CAD' });
const pct = new Intl.NumberFormat('en-CA', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const qty = new Intl.NumberFormat('en-CA', { maximumFractionDigits: 6 });
const dateTime = new Intl.DateTimeFormat('en-CA', { dateStyle: 'medium', timeStyle: 'short' });
const time = new Intl.DateTimeFormat('en-CA', { timeStyle: 'short' });
const shortDate = new Intl.DateTimeFormat('en-CA', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' });

function sign(value: number, signed: boolean): string {
  if (value < 0) return MINUS;
  return signed && value > 0 ? '+' : '';
}

/** $48,930.00 · signed: +$3,300.00 / −$570.00 / $0.00. */
export function money(value: number | null | undefined, opts: { signed?: boolean } = {}): string {
  if (value === null || value === undefined || !Number.isFinite(value)) return NONE;
  const rounded = Math.round(value * 100) / 100;
  return sign(rounded, opts.signed ?? false) + cad.format(Math.abs(rounded));
}

/** Decimal to percent: 0.557940 → 55.79% · signed: +1.11% / −1.23% / 0.00%. */
export function percent(value: number | null | undefined, opts: { signed?: boolean } = {}): string {
  if (value === null || value === undefined || !Number.isFinite(value)) return NONE;
  const hundred = Math.round(value * 10000) / 100;
  return sign(hundred, opts.signed ?? false) + pct.format(Math.abs(hundred)) + '%';
}

export function quantity(value: number): string {
  return qty.format(value);
}

/** Colour for a signed value: gain, loss, or flat (zero or unknown). */
export function tone(value: number | null | undefined): 'gain' | 'loss' | 'flat' {
  if (value === null || value === undefined || Math.round(value * 10000) === 0) return 'flat';
  return value > 0 ? 'gain' : 'loss';
}

export function dateTimeLabel(iso: string | null | undefined): string {
  if (!iso) return NONE;
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? NONE : dateTime.format(d);
}

export function timeLabel(iso: string): string {
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? NONE : time.format(d);
}

/** "2026-10-03" → "Oct 3, 2026" (dates are calendar days, so formatted in UTC). */
export function dayLabel(isoDate: string): string {
  const d = new Date(`${isoDate}T00:00:00Z`);
  return Number.isNaN(d.getTime()) ? isoDate : shortDate.format(d);
}
