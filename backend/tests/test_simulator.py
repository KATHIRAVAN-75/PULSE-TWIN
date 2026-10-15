from app.schemas import PredictionInput, ScenarioRequest
from app.simulator import estimate_risk, simulate


def test_prediction_is_deterministic_and_in_range():
    data = PredictionInput(rainfall_mm=84, temperature_c=33, outage_hours=1.5, transport_delay_min=28)
    first = estimate_risk(data)
    second = estimate_risk(data)
    assert first.score == second.score
    assert 0 <= first.score <= 100
    assert sum(round(f.weight, 2) for f in first.factors) == 1.0


def test_heavier_rain_does_not_improve_transport_access():
    calm = ScenarioRequest(rainfall_mm=0, temperature_c=28, outage_hours=0, transport_delay_min=10)
    rain = ScenarioRequest(rainfall_mm=180, temperature_c=28, outage_hours=0, transport_delay_min=10)
    assert simulate(rain).transport_delay_min > simulate(calm).transport_delay_min
    assert simulate(rain).lai < simulate(calm).lai


def test_intervention_outputs_are_recomputed():
    base = ScenarioRequest(rainfall_mm=150, temperature_c=35, outage_hours=2, transport_delay_min=45)
    buses = ScenarioRequest(**base.model_dump(exclude={"intervention"}), intervention="Extra shuttle buses")
    assert simulate(buses).transport_delay_min < simulate(base).transport_delay_min
    assert simulate(buses).estimated_cost_inr > 0
