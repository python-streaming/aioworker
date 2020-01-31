import os
import signal
from unittest import mock

from aioworker import Service, Worker

import pytest


def test_create_service(worker):
    service = Service(worker)

    assert service.worker == worker


# @pytest.mark.asyncio
# async def test_run_service(worker, event_loop):
#     service = Service(worker)
#     service.run_worker(event_loop, "pidx", ())

#     assert worker.state == Worker.RUNNING

#     childpid = os.fork()
#     os.kill(childpid, signal.SIGINT)


@pytest.mark.asyncio
async def test_stop_service():
    graceful_shutdown_mock = mock.AsyncMock("graceful_shutdown")
    forced_shutdown_mock = mock.AsyncMock("forced_shutdown")
    worker = mock.Mock(
        "worker",
        graceful_shutdown=graceful_shutdown_mock,
        forced_shutdown=forced_shutdown_mock,
    )

    service = Service(worker)

    await service.stop(signal.SIGINT)
    graceful_shutdown_mock.assert_called_once()

    await service.stop(signal.SIGQUIT)
    forced_shutdown_mock.assert_called_once()
