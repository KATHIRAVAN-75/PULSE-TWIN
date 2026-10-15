"""Deterministic, illustrative PulseTwin domain logic."""
from .schemas import PredictionInput, PredictionResponse, Factor, ScenarioRequest, ScenarioResponse

WEIGHTS = {"rainfall": 0.32, "temperature": 0.18, "power": 0.28, "transport": 0.22}
THRESHOLDS = {"rainfall": 150.0, "temperature": 42.0, "power": 6.0, "transport": 90.0}


def _category(score: int) -> str:
    if score <= 29: return "Low"
    if score <= 59: return "Medium"
    if score <= 79: return "High"
    return "Critical"


def estimate_risk(data: PredictionInput) -> PredictionResponse:
    values = [
        ("Heavy rainfall", max(0.0, min(1.0, data.rainfall_mm / THRESHOLDS["rainfall"])), WEIGHTS["rainfall"]),
        ("Heat stress", max(0.0, min(1.0, (data.temperature_c - 20.0) / (THRESHOLDS["temperature"] - 20.0))), WEIGHTS["temperature"]),
        ("Power outage", max(0.0, min(1.0, data.outage_hours / THRESHOLDS["power"])), WEIGHTS["power"]),
        ("Transport delay", max(0.0, min(1.0, data.transport_delay_min / THRESHOLDS["transport"])), WEIGHTS["transport"]),
    ]
    factors = [Factor(label=label, severity_pct=round(sev * 100), weight=weight, contribution_points=round(sev * weight * 100)) for label, sev, weight in values]
    score = max(0, min(100, round(sum(sev * weight * 100 for _, sev, weight in values))))
    top = max(factors, key=lambda factor: factor.contribution_points)
    return PredictionResponse(score=score, category=_category(score), factors=factors, explanation=f"{top.label} is the largest modeled contributor ({top.contribution_points} points). This is a deterministic rule-based estimate, not a trained AI model or calibrated probability.")


def simulate(data: ScenarioRequest) -> ScenarioResponse:
    rain = min(1.0, data.rainfall_mm / 180.0)
    heat = max(0.0, min(1.0, (data.temperature_c - 24.0) / 20.0))
    power = min(1.0, data.outage_hours / 8.0)
    delay = data.transport_delay_min + rain * 22.0
    outage = data.outage_hours
    temperature = data.temperature_c
    cost = 0
    co2 = 0
    assumptions = "No intervention applied; modeled impacts flow through town and campus twins."
    if data.intervention == "Extra shuttle buses":
        delay *= 0.68; cost = 420; co2 = 18
        assumptions = "Adds shuttle capacity; operating cost and emissions are illustrative."
    elif data.intervention == "Shift school hours":
        delay *= 0.78; cost = 80; co2 = 2
        assumptions = "Moves the arrival window away from a modeled disruption peak; staffing and family constraints are not modeled."
    elif data.intervention == "Off-peak pre-cooling":
        outage *= 0.88; temperature -= 2.5; cost = 160; co2 = 4
        assumptions = "Pre-cools priority classrooms before peak heat; assumes cooling capacity is available."
    access = max(0.0, 100.0 - delay * 0.58 - rain * 12.0 - power * 14.0)
    functionality = max(0.0, 100.0 - heat * 28.0 - outage * 8.0 - power * 12.0)
    lai = round(max(0.0, min(100.0, access * 0.62 + functionality * 0.38)))
    energy = round(820 + heat * 270 + (55 if data.intervention == "Off-peak pre-cooling" else 0))
    return ScenarioResponse(name=data.intervention, lai=lai, on_time_access_pct=round(access), classroom_functionality_pct=round(functionality), transport_delay_min=round(delay), energy_kwh=energy, estimated_cost_inr=cost, estimated_co2e_kg=co2, assumptions=assumptions)
