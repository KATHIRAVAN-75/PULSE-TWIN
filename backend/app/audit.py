"""Small in-memory SHA-256 hash-chained audit log for the demo API."""
import hashlib, json
from typing import Any

class AuditChain:
    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []

    def append(self, event_id: str, status: str, reason: str, payload_hash: str) -> dict[str, Any]:
        previous = self.entries[-1]["entry_hash"] if self.entries else "GENESIS"
        entry = {"index": len(self.entries) + 1, "event_id": event_id, "status": status, "reason": reason, "payload_hash": payload_hash, "previous_hash": previous}
        entry["entry_hash"] = hashlib.sha256(json.dumps(entry, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.entries.append(entry)
        return entry

    def verify(self) -> bool:
        previous = "GENESIS"
        for i, entry in enumerate(self.entries, start=1):
            if entry["index"] != i or entry["previous_hash"] != previous:
                return False
            unsigned = {k: v for k, v in entry.items() if k != "entry_hash"}
            expected = hashlib.sha256(json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            if expected != entry["entry_hash"]:
                return False
            previous = entry["entry_hash"]
        return True
