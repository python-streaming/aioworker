import asyncio
import logging
import typing

logger = logging.getLogger(__name__)


class Worker:

    INIT = "INIT"
    RUNNING = "RUNNING"
    STOP = "STOP"

    def __init__(
        self,
        *,
        tasks: typing.List[typing.Awaitable],
        web_server_config: typing.Dict = None,
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
        self.web_server = None
        self._loop = None
        self._state = self.INIT

        if web_server_config is not None:
            self.client_connected_cb = web_server_config.pop("client_connected_cb")
            self.host = web_server_config.pop("host", "0.0.0.0")
            self.port = web_server_config.pop("port", 8888)

        self.web_server_config = web_server_config

    @property
    def loop(self):
        return self._loop

    @property
    def state(self) -> bool:
        return self._state

    def _set_loop(self, loop) -> None:
        if self._loop is None:
            self._loop = loop

    async def run(self, loop) -> None:
        logger.debug("Running worker...")
        self._set_loop(loop)
        self._state = self.RUNNING

        if self.web_server_config is not None:
            await self.start_web_server()

        for task in self.tasks:
            asyncio.ensure_future(task(loop))

    async def on_start(self) -> None:
        logger.debug("Starting.....")

    async def stop(self) -> None:
        """
        Stop the current worker
        """
        await self.on_stop()
        self._state = self.STOP
        await asyncio.sleep(2)

    async def on_stop(self) -> None:
        logger.debug("Before Stoping.....")

    async def graceful_shutdown(self) -> None:
        logger.debug("do_graceful_shutdown")
        await self.stop()

        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

        for task in tasks:
            task.cancel()

        logger.debug(f"Cancelling {len(tasks)} outstanding tasks")

        await self.stop_web_server()

    async def forced_shutdown(self) -> None:
        logger.debug("do_forced_shutdown")
        await self.stop_web_server()

    async def start_web_server(self) -> None:
        if self.web_server is None:
            logger.debug("Starting web server")
            self.web_server = await asyncio.start_server(
                self.client_connected_cb,
                self.host,
                self.port,
                loop=self.loop,
                **self.web_server_config,
            )

    async def stop_web_server(self) -> None:
        if self.web_server is not None:
            logger.debug("Stoping web server")
            self.web_server.close()
            await self.web_server.wait_closed()
