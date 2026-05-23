from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 0.5


async def run_with_retry(
    task: Callable[[], Awaitable[T]],
    *,
    should_retry: Callable[[Exception], bool],
    policy: RetryPolicy,
) -> tuple[T, int]:
    """Run an async task with bounded retry and exponential backoff."""
    attempt = 0
    while True:
        attempt += 1
        try:
            return await task(), attempt - 1
        except Exception as exc:
            if attempt >= policy.max_attempts or not should_retry(exc):
                raise
            delay = policy.base_delay_seconds * (2 ** (attempt - 1))
            await asyncio.sleep(delay)
