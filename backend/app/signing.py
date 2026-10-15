"""Ed25519 demo event signing/verification helpers. Production keys must never live in source control."""
import base64, hashlib, json
from datetime import datetime, timezone
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from .schemas import EventPayload


def canonical_bytes(payload: EventPayload) -> bytes:
    obj = payload.model_dump(mode="json")
    # Pydantic emits an ISO timestamp; sort keys and use compact UTF-8 JSON for stable signing bytes.
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def generate_demo_keypair() -> tuple[Ed25519PrivateKey, str]:
    private_key = Ed25519PrivateKey.generate()
    public = private_key.public_key().public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
    return private_key, base64.b64encode(public).decode("ascii")


def sign_payload(payload: EventPayload, private_key: Ed25519PrivateKey) -> str:
    return base64.b64encode(private_key.sign(canonical_bytes(payload))).decode("ascii")


def verify_signature(payload: EventPayload, signature_b64: str, public_key_b64: str) -> tuple[bool, str]:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    try:
        public = Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key_b64, validate=True))
        public.verify(base64.b64decode(signature_b64, validate=True), canonical_bytes(payload))
        return True, "Ed25519 signature valid for registered demo key."
    except (ValueError, TypeError, InvalidSignature):
        return False, "Signature verification failed; event rejected."


def event_hash(payload: EventPayload) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()
