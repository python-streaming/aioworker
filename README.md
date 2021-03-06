## aioworker

A Python worker running over `asyncio`

[![Build Status](https://travis-ci.org/python-streaming/aioworker.svg?branch=master)](https://travis-ci.org/python-streaming/aioworker)
![python version](https://img.shields.io/badge/python-3.8%2B-yellowgreen)
[![License](https://img.shields.io/github/license/python-streaming/aioworker.svg)](https://github.com/python-streaming/aioworker/blob/master/LICENSE)
[![codecov](https://codecov.io/gh/python-streaming/aioworker/branch/master/graph/badge.svg)](https://codecov.io/gh/python-streaming/aioworker)


### Requirements

python 3.8+

### Installation

```bash
pip install aioworker
```

### Usage

```python
import asyncio

from aioworker import Service, Worker

async def task_1(loop):
    while True:
        print('Hello world')
        await asyncio.sleep(2)


if __name__ == '__main__':
    #  Run the server using 1 worker processes.
    Worker(tasks=[task_1]).run(workers=1)
```

or run tasks and the webserver

```python
import asyncio

from aioworker import Service, Worker


async def sleeping(loop):
    while True:
        print('Sleeping for 2 seconds...')
        await asyncio.sleep(2)


async def on_client_connect(reader, writer):
    """
    Read up tp 300 bytes of TCP. This could be parsed usign the HTTP protocol for example
    """
    data = await reader.read(300)
    print(f'TCP Server data received: {data} \n')
    writer.write(data)
    await writer.drain()
    writer.close()


if __name__ == '__main__':
    # Run the server using 1 worker processes.
    Worker(
        tasks=[sleeping],
        web_server_config={
            'client_connected_cb': on_client_connect,
        },
    )).run(workers=1)
```

### How to stop the worker

`ctrl+c`

### Default values

| Variable | Default |
|----------|---------|
| TCP server host| 0.0.0.0|
| TPC server port | 8888 |


### Examples

1. [Hello world](https://github.com/python-streaming/aioworker/blob/master/examples/hello_world.py)
2. [TCP Server](https://github.com/python-streaming/aioworker/blob/master/examples/worker_tcp_server.py)
3. [Kafka Consumer](https://github.com/python-streaming/aioworker/blob/master/examples/worker_kafka_consumer.py)


### Development

1. Clone this repo
2. Run `poetry install`
3. Test using `./scripts/test`
4. Lint automatically using `./scripts/lint`
