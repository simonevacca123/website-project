(function (root) {
  'use strict';
  function calculate({minutes, days, reduction, months = 12, rate = null}) {
    const ranges = [[minutes, 5, 180], [days, 1, 31], [reduction, 0, 100], [months, 1, 12]];
    if (ranges.some(([n, low, high]) => !Number.isFinite(n) || n < low || n > high) || (rate !== null && (!Number.isFinite(rate) || rate < 0 || rate > 10000))) throw new Error('Valori fuori intervallo');
    const before = minutes * days / 60, saved = before * reduction / 100;
    return {before, saved, after: before - saved, annual: saved * months, value: rate === null ? null : saved * rate, annualValue: rate === null ? null : saved * months * rate};
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {calculate};
  else root.Efficiency = {calculate};
})(typeof globalThis !== 'undefined' ? globalThis : this);
