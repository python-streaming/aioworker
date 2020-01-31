import asyncio
import copy
import logging
import signal
import typing

import aiotools

logger = logging.getLogger(__name__)


class Worker:

    INIT = "INIT"
    RUNNING = "RUNNING"
    STOP = "STOP"

    WEB_SERVER_HOST = "0.0.0.0"
    WEB_SERVER_PORT = 8888

    def __init__(
        self,
        *,
        tasks: typing.List[typing.Callable],
        web_server_config: typing.Dict = None,
        stop_signal=signal.SIGINT,
        timeout=0.1,
    ) -> None:
        """
        tasks (typing.List[Awaitables]): List of tasks to be run by the worker
        web_server_config (typing.Dict): Web server configuration.
            Example: {
                'client_connected_cb': client_on_connect_callback
                'host': 127.0.0.1,
                'port': 8888,
                'limit' 100,
                'family': socket.AF_UNSPEC,
                'flags': socket.AI_PASSIVE,
                'sock': None,
                'backlog': 100,
                'ssl': None,
                'reuse_address': None,
                'reuse_port': None,
                'ssl_handshake_timeout': None,
                'start_serving: True,
            }
        """
        self.tasks = tasks
        self.timeout = timeout
        self.web_server: typing.Optional[asyncio.AbstractServer] = None
        self._loop = None
        self._state = self.INIT
        self.stop_signal = stop_signal

        web_server_config = copy.deepcopy(web_server_config)
        if web_server_config is not None:
            self.client_connected_cb = web_server_config.pop("client_connected_cb")
            self.web_server_host = web_server_config.pop("host", self.WEB_SERVER_HOST)
            self.web_server_port = web_server_config.pop("port", self.WEB_SERVER_PORT)

        self.web_server_config = web_server_config

    async def do_init(args) -> None:
        logger.debug(args)

    def run(self, *args, workers: int = 1, **kwargs) -> None:
        """Public run interface."""
        aiotools.start_server(self.run_worker, num_workers=workers)

    async def _run(self, loop) -> None:
        logger.debug("Running worker...")
        self._set_loop(loop)
        await self.on_start()

        if self.web_server_config is not None:
            await self.start_web_server()

        for task in self.tasks:
            asyncio.ensure_future(task(loop))

        self._state = self.RUNNING

    @aiotools.server
    async def run_worker(self, loop, pidx, args) -> typing.AsyncGenerator:
        await self.do_init()
        asyncio.create_task(self._run(loop))

        stop_signal = yield
        await self.stop(stop_signal)

    async def stop(self, stop_signal) -> None:
        if stop_signal == self.stop_signal:
            await self.graceful_shutdown()
        else:
            await self.forced_shutdown()

    @property
    def loop(self):
        return self._loop

    @property
    def state(self) -> str:
        return self._state

    def _set_loop(self, loop) -> None:
        if self._loop is None:
            self._loop = loop

    async def on_start(self) -> None:
        logger.debug("Starting.....")

    async def _stop(self) -> None:
        """
        Set worker state to STOP
        """
        await asyncio.sleep(2)
        self._state = self.STOP

    async def on_stop(self) -> None:
        logger.debug("Before Stoping.....")

    async def graceful_shutdown(self) -> None:
        """
        Shutdown the worker:

            1. Execute on_stop
            2. Cancel tasks
            3. Stop web server if is running
            4. Execute _stop (set worker state to STOP)
        """
        logger.debug("do_graceful_shutdown")
        await self.on_stop()

        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

        for task in tasks:
            task.cancel()

        logger.debug(f"Cancelling {len(tasks)} outstanding tasks")

        await self.stop_web_server()
        await self._stop()

    async def forced_shutdown(self) -> None:
        """
        Stop webserver if is running, async tasks are not stopped
        """
        logger.debug("do_forced_shutdown")
        await self.stop_web_server()
        await self._stop()

    async def start_web_server(self) -> None:
        if self.web_server is None:
            logger.debug("Starting web server")
            self.web_server = await asyncio.start_server(
                self.client_connected_cb,
                self.web_server_host,
                self.web_server_port,
                loop=self.loop,
                **self.web_server_config,
            )

    async def stop_web_server(self) -> None:
        if self.web_server is not None:
            logger.debug("Stoping web server")
            self.web_server.close()
            await self.web_server.wait_closed()
