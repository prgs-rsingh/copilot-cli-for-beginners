"""Lightweight resilience helpers: retry with exponential backoff.

Tuning parameters
-----------------
max_retries : int
    Total number of attempts (including the first). Default: 3.
    Recommended range: 2–5. Higher values increase worst-case latency.
    Set to 1 to disable retries (first failure raises immediately).

initial_delay : float
    Seconds to wait before the second attempt. Default: 0.05 (50 ms).
    Appropriate for local-disk I/O where failures are transient.
    Increase to 0.5–2.0 for remote APIs or database calls.

backoff_factor : float
    Multiplier applied to delay on each subsequent retry. Default: 2.0 (exponential).
    Use 1.0 for a constant (linear) retry interval.

exceptions : tuple[type[Exception], ...]
    Exception types that trigger a retry. Default: (OSError,).
    Narrow this to the smallest set of known-transient exceptions.

Worst-case wait (default settings, 3 attempts):
    attempt 1 fails → wait 0.05 s
    attempt 2 fails → wait 0.10 s
    attempt 3 fails → raises

Rollback guidance
-----------------
To remove retry behaviour from a specific call site, delete the
@retry_with_backoff(...) decorator line. The underlying function is
unchanged and continues to work without it.
"""
import time
from collections.abc import Callable
from functools import wraps
from typing import Any


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 0.05,
    backoff_factor: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (OSError,),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Return a decorator that retries the wrapped function with exponential backoff.

    Parameters
    ----------
    max_retries:
        Total number of attempts (1 = no retries).
    initial_delay:
        Seconds before the second attempt.
    backoff_factor:
        Multiplier applied to delay on each subsequent retry.
    exceptions:
        Exception types that trigger a retry; all others propagate immediately.

    """
    if max_retries < 1:
        raise ValueError(f"max_retries must be >= 1, got {max_retries}")
    if initial_delay < 0:
        raise ValueError(f"initial_delay must be >= 0, got {initial_delay}")
    if backoff_factor < 1.0:
        raise ValueError(f"backoff_factor must be >= 1.0, got {backoff_factor}")

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            last_exc: Exception | None = None
            for attempt in range(1, max_retries + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt < max_retries:
                        time.sleep(delay)
                        delay *= backoff_factor
            raise last_exc  # type: ignore[misc]  # max_retries >= 1 guarantees last_exc is set

        return wrapper

    return decorator
