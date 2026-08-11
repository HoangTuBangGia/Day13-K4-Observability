from __future__ import annotations

import os
from functools import wraps
from typing import Any, Callable, TypeVar

T = TypeVar("T", bound=Callable)


class _DummyClient:
    def update_current_trace(self, **kwargs: Any) -> None:
        return None

    def update_current_generation(self, **kwargs: Any) -> None:
        return None

try:
    from langfuse import get_client, observe

    LANGFUSE_SDK_AVAILABLE = True
except ImportError:  # pragma: no cover - chỉ dùng khi chưa cài requirements
    LANGFUSE_SDK_AVAILABLE = False

    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func

        return decorator

    def get_client():
        return _DummyClient()


def get_langfuse_client():
    if not tracing_enabled():
        return _DummyClient()
    return get_client()


def tracing_enabled() -> bool:
    return LANGFUSE_SDK_AVAILABLE and bool(
        os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")
    )


def observe_when_enabled(**observe_kwargs):
    """Trace a function only when Langfuse credentials are configured."""
    def decorator(func: T) -> T:
        traced = observe(**observe_kwargs)(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            if tracing_enabled():
                return traced(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
