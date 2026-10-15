from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import PredictionInput, PredictionResponse, ScenarioRequest, ScenarioResponse, SignedEvent, VerifyResponse, EventPayload
from .simulator import estimate_risk, simulate
from .signing import generate_demo_keypair, verify_signature, event_hash
from .audit import AuditChain

app = FastAPI(title="PulseTwin API", version="1.0.0", description="Illustrative education continuity simulation API. Not an official warning service.")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
_demo_private_key, _demo_public_key_b64 = generate_demo_keypair()
_audit = AuditChain()
_last_sequence: dict[str, int] = {}

@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "illustrative-demo", "model_version": "rule-demo-1.0", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.post("/api/predict", response_model=PredictionResponse)
def predict(payload: PredictionInput):
    return estimate_risk(payload)

@app.post("/api/simulate", response_model=ScenarioResponse)
def run_simulation(payload: ScenarioRequest):
    return simulate(payload)

@app.get("/api/trust/demo-public-key")
def demo_public_key():
    return {"key_id": "pulsetwin-demo-key-1", "algorithm": "Ed25519", "public_key_b64": _demo_public_key_b64, "note": "Demo key generated at process start; not a production identity."}

@app.post("/api/trust/verify", response_model=VerifyResponse)
def verify_event(signed: SignedEvent):
    payload = signed.payload
    payload_digest = event_hash(payload)
    reason = ""
    accepted = False
    if payload.key_id != "pulsetwin-demo-key-1":
        reason = "Unknown key ID; event rejected."
    elif payload.timestamp.tzinfo is None:
        reason = "Timestamp must include a timezone; event rejected."
    elif abs((datetime.now(timezone.utc) - payload.timestamp.astimezone(timezone.utc)).total_seconds()) > 86400:
        reason = "Timestamp is stale or too far in the future; event rejected."
    elif payload.sequence_number <= _last_sequence.get(payload.twin_id, -1):
        reason = "Sequence number is repeated or replayed; event rejected."
    else:
        allowed_ranges = {"rainfall_mm": (0, 500), "temperature_c": (-10, 55), "outage_hours": (0, 72), "transport_delay_min": (0, 240), "energy_kw": (0, 10000)}
        if payload.metric not in allowed_ranges:
            reason = "Metric is not permitted; event rejected."
        elif not allowed_ranges[payload.metric][0] <= payload.value <= allowed_ranges[payload.metric][1]:
            reason = "Metric value is outside the configured range; event rejected."
        else:
            accepted, reason = verify_signature(payload, signed.signature_b64, _demo_public_key_b64)
            if accepted:
                _last_sequence[payload.twin_id] = payload.sequence_number
    _audit.append(payload.event_id, "accepted" if accepted else "rejected", reason, payload_digest)
    return VerifyResponse(accepted=accepted, reason=reason, event_hash=payload_digest, trusted_input_changed=accepted)

@app.get("/api/trust/audit")
def audit_log():
    return {"entries": _audit.entries, "chain_valid": _audit.verify(), "note": "In-memory demo chain resets when the API process restarts."}

@app.post("/api/trust/audit/verify")
def verify_audit_chain():
    return {"valid": _audit.verify(), "entries": len(_audit.entries)}

@app.post("/api/trust/sign-demo")
def sign_demo_event(payload: EventPayload):
    """Convenience endpoint for local demonstrations only; never expose this in production."""
    from .signing import sign_payload
    if payload.key_id != "pulsetwin-demo-key-1":
        raise HTTPException(status_code=400, detail="Use key_id pulsetwin-demo-key-1 for this local demo endpoint.")
    return {"payload": payload.model_dump(mode="json"), "signature_b64": sign_payload(payload, _demo_private_key), "warning": "Local demo signing endpoint; disable before production deployment."}
