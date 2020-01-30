import asyncio
import logging
import signal

import aiotools


logger = logging.getLogger(__name__)


class Service:

    def __init__(self, worker) -> None:
        self.worker = worker

    async def do_init(args):
        print(args)

    def run(self, *args, num_workers=1, **kwargs):
        aiotools.start_server(
            self.run_worker, num_workers=num_workers,
        )

    @aiotools.server
    async def run_worker(self, loop, pidx, args):
        asyncio.create_task(self.worker.run(loop))

        stop_sig = yield

        if stop_sig == signal.SIGINT:
            await self.worker.graceful_shutdown()
        else:
            await self.worker.forced_shutdown()
