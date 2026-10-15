import type { PredictionInput, ScenarioResult } from '../types';

export type TwinConfig = { id: string; name: string; type: string; expected_students: number; linked_twins: string[]; enabled_modules: string[] };
export const twinConfigs: TwinConfig[] = [
  { id: 'town', name: 'Coastal Town Twin', type: 'town', expected_students: 0, linked_twins: ['campus'], enabled_modules: ['weather', 'roads', 'transit'] },
  { id: 'campus', name: 'Riverside Campus Twin', type: 'campus', expected_students: 1200, linked_twins: ['town'], enabled_modules: ['energy', 'classrooms', 'learning_access'] },
];

export function simulate(input: PredictionInput, intervention = 'Baseline'): ScenarioResult {
  const rain = Math.min(1, input.rainfall / 180);
  const heat = Math.max(0, Math.min(1, (input.temperature - 24) / 20));
  const power = Math.min(1, input.outageHours / 8);
  const transport = Math.min(1, input.transportDelay / 100);
  let delay = input.transportDelay + rain * 22;
  let outage = input.outageHours;
  let temp = input.temperature;
  let cost = 0; let co2 = 0; let note = 'No intervention applied; modeled impacts flow through the connected town and campus twins.';
  if (intervention === 'Extra shuttle buses') { delay *= 0.68; cost = 420; co2 = 18; note = 'Adds shuttle capacity to reduce access delays; operating cost and emissions are illustrative.'; }
  if (intervention === 'Shift school hours') { delay *= 0.78; cost = 80; co2 = 2; note = 'Moves arrival window away from the modeled disruption peak; staffing and family constraints are not modeled.'; }
  if (intervention === 'Off-peak pre-cooling') { outage *= 0.88; temp -= 2.5; cost = 160; co2 = 4; note = 'Pre-cools priority classrooms before peak heat; assumes cooling capacity is available.'; }
  const access = Math.max(0, 100 - delay * 0.58 - rain * 12 - power * 14);
  const classroomFunction = Math.max(0, 100 - heat * 28 - outage * 8 - power * 12);
  const lai = Math.round(Math.max(0, Math.min(100, access * 0.62 + classroomFunction * 0.38)));
  const energyKwh = Math.round(820 + heat * 270 + (intervention === 'Off-peak pre-cooling' ? 55 : 0));
  return { name: intervention, lai, onTime: Math.round(access), classroomFunction: Math.round(classroomFunction), transportDelay: Math.round(delay), energyKwh, cost, co2, note };
}

export function makeDemoEvents() {
  return [
    { id: 'EVT-1048', time: '07:42:16', source: 'Rain gauge · North', metric: 'Rainfall', value: '84 mm / 3h', status: 'Accepted' as const, reason: 'Schema, range, sequence and demo signature checks passed.', hash: '8f3a…c91d' },
    { id: 'EVT-1047', time: '07:40:02', source: 'Campus gateway', metric: 'Grid status', value: 'Intermittent', status: 'Accepted' as const, reason: 'Trusted demo event; valid signature for registered demo key.', hash: '29b1…70aa' },
    { id: 'EVT-1046', time: '07:39:51', source: 'Road sensor · R4', metric: 'Travel delay', value: '178 min', status: 'Rejected' as const, reason: 'Signature mismatch after payload modification; excluded from trusted inputs.', hash: 'a611…3e82' },
    { id: 'EVT-1045', time: '07:38:12', source: 'Power meter · Block B', metric: 'Energy', value: '36.2 kW', status: 'Accepted' as const, reason: 'Range and freshness checks passed.', hash: '40cd…a29f' },
  ];
}
