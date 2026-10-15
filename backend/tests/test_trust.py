from datetime import datetime, timezone
from app.schemas import EventPayload
from app.signing import generate_demo_keypair, sign_payload, verify_signature, event_hash
from app.audit import AuditChain


def make_payload(value=48.5):
    return EventPayload(event_id="EVT-TEST-1", timestamp=datetime.now(timezone.utc), twin_id="town", metric="rainfall_mm", value=value, unit="mm", sequence_number=1, key_id="demo-key")


def test_signature_verification_rejects_tampering():
    private, public_b64 = generate_demo_keypair()
    original = make_payload()
    signature = sign_payload(original, private)
    assert verify_signature(original, signature, public_b64)[0] is True
    modified = original.model_copy(update={"value": 99.0})
    assert verify_signature(modified, signature, public_b64)[0] is False


def test_audit_chain_detects_mutation():
    chain = AuditChain()
    chain.append("E1", "accepted", "ok", event_hash(make_payload()))
    chain.append("E2", "rejected", "tampered", event_hash(make_payload(2)))
    assert chain.verify() is True
    chain.entries[0]["reason"] = "rewritten"
    assert chain.verify() is False
