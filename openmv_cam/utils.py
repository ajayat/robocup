import uasyncio as asyncio


class Timer:
    """A class that provides an asynchronous timer, to schedule a function execution.
    """

    def __init__(self, callback):
        self._callback = callback
        self._task = None

    def start(self, timeout: int) -> None:
        """Starts the timer and schedule the callback call.

        Args:
            timeout: in seconds, time to wait
        """
        self._task = asyncio.create_task(self._job(timeout))

    async def _job(self, timeout):
        await asyncio.sleep_ms(round(timeout*1000))
        await self._callback()

    def cancel(self) -> None:
        """Cancel the tasks if exists.
        """
        if self._task:
            self._task.cancel()
