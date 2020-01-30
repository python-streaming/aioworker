import asyncio
import logging
import typing

INIT = 'INIT'
RUNNING = 'RUNNING'
STOP = 'STOP'

logger = logging.getLogger(__name__)


class Worker:

    def __init__(self, tasks: typing.List[typing.Awaitable] = None, timeout=0.1):
        """
        Probably should be a state machine??
        """
        self._loop = None
        self.tasks = tasks
        self.timeout = timeout
        self.state = INIT

    @property
    def loop(self):
        return self._loop

    def _set_loop(self, loop) -> None:
        if self._loop is None:
            self._loop = loop

    async def run(self, loop) -> None:
        logger.debug('Running worker...')
        self._set_loop(loop)
        self.state = RUNNING

        for task in self.tasks:
            asyncio.ensure_future(task(loop))

    async def on_start(self):
        logger.debug('Starting.....')

    async def stop(self):
        """
        Stop the current worker
        """
        await self.on_stop()
        self.state = STOP
        await asyncio.sleep(2)

    async def on_stop(self):
        logger.debug('Before Stoping.....')

    async def graceful_shutdown(self):
        logger.debug('do_graceful_shutdown')
        await self.stop()

        tasks = [
            t for t in asyncio.all_tasks() if t is not
            asyncio.current_task()
        ]

        for task in tasks:
            task.cancel()

        logger.debug(f'Cancelling {len(tasks)} outstanding tasks')

    async def forced_shutdown(self):
        logger.debug('do_forced_shutdown')
