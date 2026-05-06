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

deadline : float | None
    Total wall-time budget in seconds for all attempts (including sleeps).
    Default: None (no deadline — retries run until max_retries is exhausted).
    When set, a TimeoutError is raised as soon as elapsed time >= deadline,
    regardless of how many retries remain. Set conservatively: typical disk
    I/O retries (3 attempts, 50 ms initial) complete in < 200 ms; a deadline
    of 5.0 s gives ample headroom while protecting against indefinite blocking.

Worst-case wait (default settings, 3 attempts):
    attempt 1 fails → wait 0.05 s
    attempt 2 fails → wait 0.10 s
    attempt 3 fails → raises

With deadline=5.0 s added:
    Same as above, but raises TimeoutError if any attempt + sleep exceeds 5 s.

Rollback guidance
-----------------
To remove retry behaviour from a specific call site, delete the
@retry_with_backoff(...) decorator line. The underlying function is
unchanged and continues to work without it.

To remove the deadline from a specific call site, remove the deadline=
argument from the decorator. Behaviour reverts to unbounded retry.
"""
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

from logging_config import get_logger

logger = get_logger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 0.05,
    backoff_factor: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (OSError,),
    deadline: float | None = None,
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
    deadline:
        Total wall-time budget in seconds. TimeoutError raised when exceeded.

    """
    if max_retries < 1:
        raise ValueError(f"max_retries must be >= 1, got {max_retries}")
    if initial_delay < 0:
        raise ValueError(f"initial_delay must be >= 0, got {initial_delay}")
    if backoff_factor < 1.0:
        raise ValueError(f"backoff_factor must be >= 1.0, got {backoff_factor}")
    if deadline is not None and deadline <= 0:
        raise ValueError(f"deadline must be > 0 when set, got {deadline}")

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            last_exc: Exception | None = None
            start = time.monotonic()
            for attempt in range(1, max_retries + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    elapsed = time.monotonic() - start
                    # Check deadline before deciding whether to retry or sleep.
                    if deadline is not None and elapsed >= deadline:
                        logger.warning(
                            "retry.deadline_exceeded",
                            extra={
                                "fn": getattr(fn, "__name__", repr(fn)),
                                "elapsed_s": round(elapsed, 3),
                                "deadline_s": deadline,
                                "attempt": attempt,
                                "error": str(exc),
                            },
                        )
                        raise TimeoutError(
                            f"Deadline of {deadline}s exceeded after {elapsed:.3f}s "
                            f"({attempt} attempt(s)) in {getattr(fn, '__name__', repr(fn))}"
                        ) from exc
                    if attempt < max_retries:
                        # Cap sleep to whatever remains of the deadline budget.
                        sleep_time = delay
                        if deadline is not None:
                            remaining = deadline - elapsed
                            sleep_time = min(delay, max(remaining, 0.0))
                        logger.warning(
                            "retry.attempt",
                            extra={
                                "fn": getattr(fn, "__name__", repr(fn)),
                                "attempt": attempt,
                                "max": max_retries,
                                "delay_s": sleep_time,
                                "error": str(exc),
                            },
                        )
                        time.sleep(sleep_time)
                        delay *= backoff_factor
                    else:
                        logger.exception(
                            "retry.exhausted",
                            extra={
                                "fn": getattr(fn, "__name__", repr(fn)),
                                "attempts": max_retries,
                                "error": str(last_exc),
                            },
                        )
            raise last_exc  # type: ignore[misc]  # max_retries >= 1 guarantees last_exc is set

        return wrapper

    return decorator
