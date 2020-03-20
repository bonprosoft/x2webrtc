import asyncio
import time
from typing import Optional


class Timer:
    def __init__(self, fps: int):
        self._last: Optional[float] = None
        self._duration = 1.0 / fps

    def _calc_wait_sec(self) -> float:
        current = time.time()
        if self._last is not None:
            diff = current - self._last
            self._last += self._duration

            if diff < self._duration:
                return self._duration - diff
            else:
                return 0.0
        else:
            self._last = current
            return 0.0

    def reset_throttle(self) -> None:
        self._last = time.time()

    async def wait_async(self) -> None:
        to_wait = self._calc_wait_sec()
        if to_wait > 0.0:
            await asyncio.sleep(to_wait)

    def wait(self) -> None:
        to_wait = self._calc_wait_sec()
        if to_wait > 0.0:
            time.sleep(to_wait)
