import asyncio
import logging

INIT = 'INIT'
RUNNING = 'RUNNING'
STOP = 'STOP'

logger = logging.getLogger(__name__)


class Worker:

    def __init__(self, loop, task, on_start=None, on_stop=None, timeout=0.1):
        """
        Probably should be a state machine??
        """
        self.loop = loop
        self.task = task
        self.timeout = timeout
        self.state = INIT

    async def run(self):
        self.state = RUNNING
        asyncio.ensure_future(self.task)

        # self.loop.run_until_complete(self.task)
        # self.loop.run_until_complete(consume(self.loop))

        # while self.state == "running":
        #     print("Worker runnnig...")
        #     await consume(self.loop)
        #     await asyncio.sleep(self.timeout)

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
