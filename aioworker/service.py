import asyncio
import logging
import signal
import typing

import aiotools

logger = logging.getLogger(__name__)


class Service:
    def __init__(self, worker, stop_signal=signal.SIGINT) -> None:
        self.worker = worker
        self.stop_signal = stop_signal

    async def do_init(args) -> None:
        logger.debug(args)

    def run(self, *args, num_workers: int = 1, **kwargs) -> None:
        aiotools.start_server(self.run_worker, num_workers=num_workers)

    @aiotools.server
    async def run_worker(self, loop, pidx, args) -> typing.AsyncGenerator:
        await self.do_init()
        asyncio.create_task(self.worker.run(loop))

        stop_signal = yield
        await self.stop(stop_signal)

    async def stop(self, stop_signal) -> None:
        if stop_signal == self.stop_signal:
            await self.worker.graceful_shutdown()
        else:
            await self.worker.forced_shutdown()
