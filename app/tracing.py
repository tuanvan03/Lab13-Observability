from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any

from dotenv import load_dotenv
load_dotenv()

os.environ["LANGFUSE_PUBLIC_KEY"] = os.getenv("LANGFUSE_PUBLIC_KEY", "")
os.environ["LANGFUSE_SECRET_KEY"] = os.getenv("LANGFUSE_SECRET_KEY", "")
os.environ["LANGFUSE_HOST"] = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

try:
    from langfuse import Langfuse, observe
    langfuse_client = Langfuse()

except Exception:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    class _DummyObs:
        def update(self, **kwargs: Any) -> None:
            return None

    class _DummyClient:
        def update_current_trace(self, **kwargs: Any) -> None:
            return None

        def update_current_observation(self, **kwargs: Any) -> None:
            return None

        def update_current_generation(self, **kwargs: Any) -> None:
            return None

        @contextmanager
        def start_as_current_observation(self, *args: Any, **kwargs: Any):
            yield _DummyObs()

        def flush(self) -> None:
            return None

    langfuse_client = _DummyClient()


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
