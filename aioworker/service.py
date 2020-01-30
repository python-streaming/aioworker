import asyncio
import logging
import signal

import aiotools


logger = logging.getLogger(__name__)


class Service:

    def __init__(self, worker, include_web_server: bool = False) -> None:
        self.worker = worker
        self.include_web_server = include_web_server
        self.web_server = None

    async def do_init(args):
        print(args)

    def run(self, *args, num_workers=1, **kwargs):
        aiotools.start_server(
            self.run_worker, num_workers=num_workers,
        )

    @aiotools.server
    async def run_worker(self, loop, pidx, args):
        asyncio.create_task(self.worker.run(loop))

        # if self.include_web_server:
        #     await self.start_web_server(loop)

        stop_sig = yield

        if stop_sig == signal.SIGINT:
            await self.worker.graceful_shutdown()
        else:
            await self.worker.forced_shutdown()
