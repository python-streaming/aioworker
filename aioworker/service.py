import asyncio
import logging
import signal
import typing

import aiotools

logger = logging.getLogger(__name__)


class Service:
    def __init__(self, worker) -> None:
        self.worker = worker

    async def do_init(args) -> None:
        logger.debug(args)

    def run(self, *args, num_workers: int = 1, **kwargs) -> None:
        aiotools.start_server(self.run_worker, num_workers=num_workers)

    @aiotools.server
    async def run_worker(self, loop, pidx, args) -> typing.AsyncGenerator:
        asyncio.create_task(self.worker.run(loop))

        stop_sig = yield

        if stop_sig == signal.SIGINT:
            await self.worker.graceful_shutdown()
        else:
            await self.worker.forced_shutdown()
