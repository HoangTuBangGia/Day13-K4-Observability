from __future__ import annotations

import json

from app import audit


def test_audit_log_hashes_actor_and_records_control_action(monkeypatch, tmp_path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setattr(audit, "AUDIT_LOG_PATH", audit_path)

    record = audit.record_incident_action(
        actor_id="2A202601204",
        correlation_id="req-12345678",
        action="enable",
        incident="rag_slow",
        outcome="success",
    )

    persisted = json.loads(audit_path.read_text(encoding="utf-8"))
    assert persisted == record
    assert persisted["actor_id_hash"] != "2A202601204"
    assert persisted["correlation_id"] == "req-12345678"
    assert persisted["action"] == "enable"
    assert persisted["target"] == "rag_slow"
