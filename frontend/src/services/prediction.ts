import type { PredictionInput, PredictionResult, Severity } from '../types';

export const riskConfig = {
  weights: { rainfall: 0.32, temperature: 0.18, outageHours: 0.28, transportDelay: 0.22 },
  thresholds: { rainfall: 150, temperature: 42, outageHours: 6, transportDelay: 90 },
  categories: [{ max: 29, name: 'Low' }, { max: 59, name: 'Medium' }, { max: 79, name: 'High' }, { max: 100, name: 'Critical' }] as const,
};

export function validatePredictionInput(input: PredictionInput): string[] {
  const checks: [keyof PredictionInput, string, number, number][] = [
    ['rainfall', 'Rainfall', 0, 500], ['temperature', 'Temperature', -10, 55],
    ['outageHours', 'Power outage duration', 0, 72], ['transportDelay', 'Transport delay', 0, 240],
  ];
  const errors: string[] = [];
  for (const [key, label, min, max] of checks) {
    const value = input[key];
    if (!Number.isFinite(value)) errors.push(`${label} must be a valid number.`);
    else if (value < min || value > max) errors.push(`${label} must be between ${min} and ${max}${key === 'rainfall' ? ' mm' : key === 'temperature' ? ' °C' : key === 'outageHours' ? ' hours' : ' minutes'}.`);
  }
  return errors;
}

export function estimateRisk(input: PredictionInput): PredictionResult {
  const normalizedFactors = [
    { key: 'rainfall' as const, label: 'Heavy rainfall', value: input.rainfall, weight: riskConfig.weights.rainfall, threshold: riskConfig.thresholds.rainfall },
    { key: 'temperature' as const, label: 'Heat stress', value: input.temperature, weight: riskConfig.weights.temperature, threshold: riskConfig.thresholds.temperature, floor: 20 },
    { key: 'outageHours' as const, label: 'Power outage', value: input.outageHours, weight: riskConfig.weights.outageHours, threshold: riskConfig.thresholds.outageHours },
    { key: 'transportDelay' as const, label: 'Transport delay', value: input.transportDelay, weight: riskConfig.weights.transportDelay, threshold: riskConfig.thresholds.transportDelay },
  ].map(f => {
    const severity = f.key === 'temperature' ? Math.max(0, Math.min(1, (f.value - (f.floor ?? 0)) / (f.threshold - (f.floor ?? 0)))) : Math.max(0, Math.min(1, f.value / f.threshold));
    return { label: f.label, value: f.value, normalized: severity, severity: Math.round(severity * 100), weight: f.weight, contribution: Math.round(severity * f.weight * 100) };
  });
  const factors = normalizedFactors.map(({ normalized: _normalized, ...factor }) => factor);
  const score = Math.round(normalizedFactors.reduce((sum, f) => sum + f.normalized * f.weight * 100, 0));
  const category = (riskConfig.categories.find(c => score <= c.max)?.name ?? 'Critical') as Severity;
  const top = [...factors].sort((a, b) => b.contribution - a.contribution)[0];
  return { score, category, factors, explanation: `${top.label} is the largest modeled contributor (${top.contribution} points). This transparent rule-based estimate is illustrative and is not a trained AI model or a calibrated probability.`, createdAt: new Date().toISOString() };
}
