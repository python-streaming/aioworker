import asyncio

from aioworker import Service, Worker


async def task_1(loop):
    while True:
        print('Hello world')
        await asyncio.sleep(2)


if __name__ == '__main__':
    #  Run the server using 1 worker processes.
    Service(Worker(
        tasks=[task_1],
    )).run(num_workers=1)
