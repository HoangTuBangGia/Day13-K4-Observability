from app import mock_rag


def test_retrieval_logs_latency_and_incident(monkeypatch) -> None:
    events: list[tuple[str, dict]] = []
    monkeypatch.setattr(mock_rag.log, "info", lambda event, **kwargs: events.append((event, kwargs)))
    monkeypatch.setitem(mock_rag.STATE, "rag_slow", False)

    docs = mock_rag.retrieve.__wrapped__("Explain monitoring")

    assert docs
    assert events[-1][0] == "retrieval_completed"
    assert events[-1][1]["service"] == "rag"
    assert events[-1][1]["latency_ms"] >= 0
    assert events[-1][1]["incident"] is None
