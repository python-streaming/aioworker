import asyncio
import logging
import logging.config
import os

from aiokafka import AIOKafkaConsumer

from aioworker import Service, Worker

import conf

logging.config.dictConfig(conf.LOGGING_CONFIG)

logger = logging.getLogger(__name__)

BOOTSTRAP_SERVERS = os.getenv('BOOTSTRAP_SERVERS', '0.0.0.0:9092')
TOPIC = os.getenv('BOOTSTRAP_SERVERS', 'test-topic-worker')
GROUP_ID = os.getenv('GROUP_ID', 'test-consumer-group')
AUTO_OFFSET_RESET = os.getenv('AUTO_OFFSET_RESET', 'earliest')


async def consume_from_kafka(loop):
    logger.debug('Task Consuming from kafka initiated...')
    consumer = AIOKafkaConsumer(
        TOPIC, loop=loop,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id=GROUP_ID, auto_offset_reset=AUTO_OFFSET_RESET)

    # Get cluster layout and join group `my-group`await consumer.start()
    await consumer.start()

    try:
        # Consume messages
        async for msg in consumer:
            logger.debug(f'Task Consuming from kafka')
            logger.debug(f'Topic: {msg.topic}, Partition: {msg.partition}, Offset: {msg.offset},'
                         f' Key: {msg.key}, Value: {msg.value}, Timestamp: {msg.timestamp}\n')
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()


async def hello_world(loop):
    while True:
        print('Hello world...')
        await asyncio.sleep(2)


async def client_connect(reader, writer):
    """
    Read up tp 300 bytes of TCP. This could be parsed usign the HTTP protocol for example
    """
    data = await reader.read(300)
    logger.debug(f'TCP Server data received: {data} \n')
    writer.write(data)
    await writer.drain()
    writer.close()


if __name__ == '__main__':
    # Run the server using 1 worker processes.
    logging.config.dictConfig(conf.LOGGING_CONFIG)

    Service(Worker(
        tasks=[hello_world],
        web_server_config={
            'client_connected_cb': client_connect,
        },
    )).run(num_workers=1)
