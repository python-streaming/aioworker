import os

from aiokafka import AIOKafkaConsumer


BOOTSTRAP_SERVERS = os.getenv('BOOTSTRAP_SERVERS', '0.0.0.0:9092')
TOPIC = os.getenv('BOOTSTRAP_SERVERS', 'test-topic-worker')
GROUP_ID = os.getenv('GROUP_ID', 'test-consumer-group')
AUTO_OFFSET_RESET = os.getenv('AUTO_OFFSET_RESET', 'earliest')


# The tasks must be outside the aio_worker folder

async def consume_from_kafka(loop):
    print('Task Consuming from kafka initiated...')
    consumer = AIOKafkaConsumer(
        TOPIC, loop=loop,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id=GROUP_ID, auto_offset_reset=AUTO_OFFSET_RESET)

    # Get cluster layout and join group `my-group`await consumer.start()
    await consumer.start()

    try:
        # Consume messages
        async for msg in consumer:
            print(f'Task Consuming from kafka')
            print(f'Topic: {msg.topic}, Partition: {msg.partition}, Offset: {msg.offset},'
                  f' Key: {msg.key}, Value: {msg.value}, Timestamp: {msg.timestamp}\n')
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()


async def tcp_server(reader, writer):
    """
    Read up tp 300 bytes of TCP. This could be parsed usign the HTTP protocol for example
    """
    data = await reader.read(300)
    logger.debug(f'TCP Server data received: {data} \n')
    writer.write(data)
    await writer.drain()
    writer.close()


@aiotools.server
async def tcp_server_and_worker(loop, pidx, args):
    await do_init(args)

    # worker tasks
    worker_tasks = asyncio.gather(
        tasks.consume_from_kafka(loop),
    )

    worker = Worker(loop, worker_tasks)
    asyncio.create_task(worker.run())

    logger.debug(f'[{pidx}] started')
    server = await asyncio.start_server(
        tasks.tcp_server, '0.0.0.0', 8888,
        reuse_port=True, loop=loop)

    stop_sig = yield

    if stop_sig == signal.SIGINT:
        await worker.graceful_shutdown()
    else:
        await worker.forced_shutdown()

    server.close()
    await server.wait_closed()
    logger.debug(f'[{pidx}] terminated')



if __name__ == '__main__':
    #  Run the server using 1 worker processes.
    service.Service(worker.Worker(
        [task_1, task_2],
    )).run(num_workers=1)
