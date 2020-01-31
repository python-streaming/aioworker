import signal
from unittest import mock

import pytest

from aioworker import Service, Worker


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
async def test_stop_worker():
    worker = Worker(tasks=[])

    graceful_shutdown_mock = mock.AsyncMock("graceful_shutdown")
    forced_shutdown_mock = mock.AsyncMock("forced_shutdown")
    with mock.patch(worker, "graceful_shutdown_mock", graceful_shutdown_mock) as m:
        with mock.patch(worker, "forced_shutdown_mock", forced_shutdown_mock) as m2:
            await worker.stop(signal.SIGINT)
            graceful_shutdown_mock.assert_called_once()

            await worker.stop(signal.SIGQUIT)
            forced_shutdown_mock.assert_called_once()
