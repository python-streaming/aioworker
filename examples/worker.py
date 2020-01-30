import asyncio

from aioworker import service, worker


async def task_2(args):
    print(f'Initiation with {args}')


async def task_1(loop):
    while True:
        print('Sleeping for 2 seconds...')
        await asyncio.sleep(2)


if __name__ == '__main__':
    #  Run the server using 1 worker processes.
    service.Service(worker.Worker(
        [task_1, task_2],
    )).run(num_workers=1)
