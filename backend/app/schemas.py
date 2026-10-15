from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

class PredictionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rainfall_mm: float = Field(ge=0, le=500)
    temperature_c: float = Field(ge=-10, le=55)
    outage_hours: float = Field(ge=0, le=72)
    transport_delay_min: float = Field(ge=0, le=240)

class Factor(BaseModel):
    label: str
    severity_pct: int
    weight: float
    contribution_points: int

class PredictionResponse(BaseModel):
    score: int
    category: Literal["Low", "Medium", "High", "Critical"]
    factors: list[Factor]
    explanation: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_version: str = "rule-demo-1.0"
    illustrative: bool = True

class ScenarioRequest(PredictionInput):
    intervention: Literal["Baseline", "Extra shuttle buses", "Shift school hours", "Off-peak pre-cooling"] = "Baseline"

class ScenarioResponse(BaseModel):
    name: str
    lai: int
    on_time_access_pct: int
    classroom_functionality_pct: int
    transport_delay_min: int
    energy_kwh: int
    estimated_cost_inr: int
    estimated_co2e_kg: int
    assumptions: str
    illustrative: bool = True

class EventPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: str = Field(min_length=1, max_length=100)
    timestamp: datetime
    twin_id: str = Field(min_length=1, max_length=100)
    metric: str = Field(min_length=1, max_length=80)
    value: float
    unit: str = Field(min_length=1, max_length=30)
    sequence_number: int = Field(ge=0)
    key_id: str = Field(min_length=1, max_length=100)
    schema_version: str = "1.0"

class SignedEvent(BaseModel):
    payload: EventPayload
    signature_b64: str

class VerifyResponse(BaseModel):
    accepted: bool
    reason: str
    event_hash: str
    trusted_input_changed: bool = False
