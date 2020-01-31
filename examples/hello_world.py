import asyncio

from aioworker import Worker


async def task_1(loop):
    while True:
        print("Hello world")
        await asyncio.sleep(2)


if __name__ == "__main__":
    #  Run the server using 1 worker processes.
    Worker(tasks=[task_1]).run(workers=1)
