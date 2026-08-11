from __future__ import annotations

from app.logging_config import scrub_event
from app.pii import hash_user_id


def test_scrub_event_redacts_nested_pii() -> None:
    event = {
        "event": "request_received",
        "payload": {
            "contact": "student@vinuni.edu.vn",
            "items": ["090 123 4567", {"passport": "B1234567"}],
        },
    }

    scrubbed = scrub_event(None, "info", event)

    assert "student@" not in str(scrubbed)
    assert "090 123 4567" not in str(scrubbed)
    assert "B1234567" not in str(scrubbed)


def test_user_hash_is_stable_and_does_not_expose_raw_id() -> None:
    user_id = "2A202601204"
    assert hash_user_id(user_id) == hash_user_id(user_id)
    assert user_id not in hash_user_id(user_id)
