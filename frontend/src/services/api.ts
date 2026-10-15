/** Optional FastAPI adapter. The browser demo intentionally uses local deterministic data by default. */
import type { PredictionInput, PredictionResult, ScenarioResult } from '../types';

const baseUrl = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8000';

export interface PulseTwinService {
  predict(input: PredictionInput): Promise<PredictionResult>;
  simulate(input: PredictionInput, intervention?: string): Promise<ScenarioResult>;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  });
  if (!response.ok) {
    const detail = await response.text().catch(() => 'Unknown API error');
    throw new Error(`PulseTwin API ${response.status}: ${detail}`);
  }
  return response.json() as Promise<T>;
}

export const apiService: PulseTwinService = {
  async predict(input) {
    const result = await post<{score:number;category:PredictionResult['category'];factors:{label:string;severity_pct:number;weight:number;contribution_points:number}[];explanation:string;created_at:string}>('/api/predict', {
      rainfall_mm: input.rainfall, temperature_c: input.temperature, outage_hours: input.outageHours, transport_delay_min: input.transportDelay,
    });
    return { score: result.score, category: result.category, explanation: result.explanation, createdAt: result.created_at, factors: result.factors.map(f => ({label:f.label, severity:f.severity_pct, weight:f.weight, contribution:f.contribution_points, value: f.label === 'Heavy rainfall' ? input.rainfall : f.label === 'Heat stress' ? input.temperature : f.label === 'Power outage' ? input.outageHours : input.transportDelay})) };
  },
  async simulate(input, intervention = 'Baseline') {
    const result = await post<{name:string;lai:number;on_time_access_pct:number;classroom_functionality_pct:number;transport_delay_min:number;energy_kwh:number;estimated_cost_inr:number;estimated_co2e_kg:number;assumptions:string}>('/api/simulate', {
      rainfall_mm: input.rainfall, temperature_c: input.temperature, outage_hours: input.outageHours, transport_delay_min: input.transportDelay, intervention,
    });
    return { name:result.name, lai:result.lai, onTime:result.on_time_access_pct, classroomFunction:result.classroom_functionality_pct, transportDelay:result.transport_delay_min, energyKwh:result.energy_kwh, cost:result.estimated_cost_inr, co2:result.estimated_co2e_kg, note:result.assumptions };
  },
};
