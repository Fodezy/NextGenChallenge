import { describe, expect, it } from 'vitest';
import { dayLabel, money, percent, tone } from './format';

describe('money', () => {
  it('formats CAD with thousands separators', () => {
    expect(money(48930)).toBe('$48,930.00');
    expect(money(72.1)).toBe('$72.10');
  });
  it('signs gains with + and losses with a real minus (U+2212)', () => {
    expect(money(3300, { signed: true })).toBe('+$3,300.00');
    expect(money(-570, { signed: true })).toBe('−$570.00');
    expect(money(-570)).toBe('−$570.00');
  });
  it('shows zero without a sign, even when signed', () => {
    expect(money(0, { signed: true })).toBe('$0.00');
    expect(money(-0.001, { signed: true })).toBe('$0.00');
  });
  it('shows — for null, undefined and non-finite values', () => {
    expect(money(null)).toBe('—');
    expect(money(undefined)).toBe('—');
    expect(money(Number.NaN)).toBe('—');
  });
});

describe('percent', () => {
  it('turns decimals into percentages with 2 decimals', () => {
    expect(percent(0.55794)).toBe('55.79%');
    expect(percent(1)).toBe('100.00%');
  });
  it('signs changes', () => {
    expect(percent(2.5 / 225, { signed: true })).toBe('+1.11%');
    expect(percent(-0.9 / 73, { signed: true })).toBe('−1.23%');
    expect(percent(0, { signed: true })).toBe('0.00%');
  });
  it('shows — for null (e.g. zero previous close)', () => {
    expect(percent(null, { signed: true })).toBe('—');
  });
});

describe('tone', () => {
  it('classifies gains, losses and flat values', () => {
    expect(tone(30)).toBe('gain');
    expect(tone(-270)).toBe('loss');
    expect(tone(0)).toBe('flat');
    expect(tone(null)).toBe('flat');
  });
});

describe('dayLabel', () => {
  it('formats a calendar date without shifting it across time zones', () => {
    expect(dayLabel('2026-01-01')).toBe('Jan 1, 2026');
  });
});
