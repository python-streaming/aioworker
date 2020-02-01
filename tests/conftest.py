import asyncio

import pytest

from aioworker import Worker


async def task_1(loop):
    while True:
        print("hello world")
        await asyncio.sleep(2)


async def client_connected_cb(reader, writer):
    """
    Read up tp 300 bytes of TCP. This could be parsed usign
    the HTTP protocol for example
    """
    data = await reader.read(100)
    writer.write(data)
    await writer.drain()
    writer.close()


@pytest.fixture
def tasks():
    return [task_1]


@pytest.fixture
def web_server_config():
    return {"client_connected_cb": "", "host": "127.0.0.1", "port": 8000}


@pytest.yield_fixture()
def worker():
    return Worker(tasks=[])


@pytest.yield_fixture()
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
