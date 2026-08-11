from __future__ import annotations

import time

from .incidents import STATE
from .logging_config import get_logger
from .tracing import observe_when_enabled

log = get_logger()

CORPUS = {
    "refund": ["Refunds are available within 7 days with proof of purchase."],
    "monitoring": ["Metrics detect incidents, traces localize them, logs explain root cause."],
    "policy": ["Do not expose PII in logs. Use sanitized summaries only."],
}


@observe_when_enabled(name="rag.retrieve", as_type="span", capture_input=False, capture_output=False)
def retrieve(message: str) -> list[str]:
    started = time.perf_counter()
    if STATE["tool_fail"]:
        raise RuntimeError("Vector store timeout")
    if STATE["rag_slow"]:
        time.sleep(2.5)
    lowered = message.lower()
    for key, docs in CORPUS.items():
        if key in lowered:
            log.info(
                "retrieval_completed",
                service="rag",
                latency_ms=int((time.perf_counter() - started) * 1000),
                doc_count=len(docs),
                incident="rag_slow" if STATE["rag_slow"] else None,
            )
            return docs
    docs = ["No domain document matched. Use general fallback answer."]
    log.info(
        "retrieval_completed",
        service="rag",
        latency_ms=int((time.perf_counter() - started) * 1000),
        doc_count=len(docs),
        incident="rag_slow" if STATE["rag_slow"] else None,
    )
    return docs
