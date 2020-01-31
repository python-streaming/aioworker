import pytest

from aioworker import Worker


def test_create_worker(tasks):
    worker = Worker(tasks=tasks)

    assert worker.state == Worker.INIT
    assert worker.web_server is None
    assert worker.loop is None
    assert worker.web_server_config is None


def test_create_worker_with_web_server(tasks, web_server_config):
    worker = Worker(tasks=tasks, web_server_config=web_server_config,)

    assert worker.client_connected_cb == web_server_config["client_connected_cb"]
    assert worker.web_server_host == web_server_config["host"]
    assert worker.web_server_port == web_server_config["port"]


@pytest.mark.asyncio
async def test_graceful_shutdown(event_loop, tasks):
    worker = Worker(tasks=tasks)

    await worker.run(event_loop)
    assert worker.state == Worker.RUNNING

    await worker.graceful_shutdown()
    assert worker.state == Worker.STOP


@pytest.mark.asyncio
async def test_run_with_web_server(event_loop, tasks, web_server_config):
    worker = Worker(tasks=[], web_server_config=web_server_config,)

    await worker.run(event_loop)
    assert worker.state == Worker.RUNNING
    assert worker.web_server

    await worker.graceful_shutdown()
    assert worker.state == Worker.STOP
    assert not worker.web_server.is_serving()


@pytest.mark.asyncio
async def test_forced_shutdown(event_loop, web_server_config):
    worker = Worker(tasks=[], web_server_config=web_server_config,)

    await worker.run(event_loop)
    assert worker.state == Worker.RUNNING

    await worker.forced_shutdown()
    assert worker.state == Worker.STOP
