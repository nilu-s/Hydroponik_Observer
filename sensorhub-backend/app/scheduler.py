from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from .config import log_event

IntervalProvider = Callable[[], float]
WorkFn = Callable[[], Awaitable[None]]


async def run_periodic(
    task_name: str,
    interval_provider: IntervalProvider,
    work: WorkFn,
    min_sleep_sec: float = 0.2,
) -> None:
    """Run a task forever with a dynamic polling interval."""
    while True:
        try:
            await work()
        except Exception as exc:
            log_event("loop.error", loop=task_name, error=str(exc))
        interval = max(min_sleep_sec, float(interval_provider()))
        await asyncio.sleep(interval)


class LoopRegistry:
    def __init__(self) -> None:
        self._tasks: dict[str, asyncio.Task[None]] = {}

    def start(self, name: str, coro: Awaitable[None]) -> asyncio.Task[None]:
        task = asyncio.create_task(coro)
        self._tasks[name] = task
        return task

    def stop(self, name: str) -> None:
        task = self._tasks.pop(name, None)
        if task:
            task.cancel()

    def stop_all(self) -> None:
        for name in list(self._tasks.keys()):
            self.stop(name)

    def status(self) -> list[dict[str, Any]]:
        return [
            {"name": name, "done": task.done(), "cancelled": task.cancelled()}
            for name, task in self._tasks.items()
        ]
