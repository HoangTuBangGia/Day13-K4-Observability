from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from .pii import hash_user_id, scrub_text

AUDIT_LOG_PATH = Path(os.getenv("AUDIT_LOG_PATH", "data/audit.jsonl"))


def record_incident_action(
    *, actor_id: str, correlation_id: str, action: str, incident: str, outcome: str
) -> dict[str, str]:
    """Append an immutable, PII-safe record for a control-plane action."""
    record = {
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "event": "incident_control",
        "actor_id_hash": hash_user_id(actor_id),
        "correlation_id": correlation_id,
        "action": action,
        "target": scrub_text(incident),
        "outcome": outcome,
    }
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record
