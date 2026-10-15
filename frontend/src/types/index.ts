export type Severity = 'Low' | 'Medium' | 'High' | 'Critical';
export type PredictionInput = { rainfall: number; temperature: number; outageHours: number; transportDelay: number };
export type PredictionFactor = { label: string; value: number; severity: number; weight: number; contribution: number };
export type PredictionResult = { score: number; category: Severity; factors: PredictionFactor[]; explanation: string; createdAt: string };
export type ScenarioResult = { name: string; lai: number; onTime: number; classroomFunction: number; transportDelay: number; energyKwh: number; cost: number; co2: number; note: string };
export type SensorEvent = { id: string; time: string; source: string; metric: string; value: string; status: 'Accepted' | 'Rejected'; reason: string; hash: string };
