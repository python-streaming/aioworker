import asyncio
import logging
import logging.config
import signal

import aiotools

import conf

from src import tasks
from src.worker import Worker


logging.config.dictConfig(conf.LOGGING_CONFIG)

logger = logging.getLogger(__name__)


async def do_init(args):
    logger.debug(f'Initiation with {args}')


@aiotools.server
async def tcp_server_and_worker(loop, pidx, args):
    await do_init(args)

    # worker tasks
    worker_tasks = asyncio.gather(
        tasks.consume_from_kafka(loop),
    )

    worker = Worker(loop, worker_tasks)
    asyncio.create_task(worker.run())

    logger.debug(f'[{pidx}] started')
    server = await asyncio.start_server(
        tasks.tcp_server, '0.0.0.0', 8888,
        reuse_port=True, loop=loop)

    stop_sig = yield

    if stop_sig == signal.SIGINT:
        await worker.graceful_shutdown()
    else:
        await worker.forced_shutdown()

    server.close()
    await server.wait_closed()
    logger.debug(f'[{pidx}] terminated')


if __name__ == '__main__':
    #  Run the server using 1 worker processes.
    # Args should be read from Command Line
    aiotools.start_server(tcp_server_and_worker, num_workers=1)
